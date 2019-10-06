import time
import random
import hashlib
from alipay import AliPay

from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse

from Buyer import models, forms
from Seller.models import GoodsType, Goods
from Qshop.settings import ALIPAY_PUBLIC, APP_PRIVATE, ALIPAY_URL


def set_pwd(password):
    SALT = b'bestwish'
    md5 = hashlib.md5(SALT)
    md5.update(password.encode('utf-8'))
    ret = md5.hexdigest()
    return ret


def login_valid(func):
    def inner(request, *args, **kwargs):
        cookie_email = request.COOKIES.get('buyer_user_email')
        session_email = request.session.get('buyer_user_email')
        if cookie_email and cookie_email == session_email:
            return func(request, *args, **kwargs)
        else:
            return redirect('/seller/login/')

    return inner


def random_str():
    string = 'abcdefghigklmnopqrstuvwxyz'
    ret = ''
    for i in range(4):
        ret += random.choice(string)
    return ret

# Create your views here.


def register(request):
    err_msg = ''
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            password = request.POST.get('password')
            repassword = request.POST.get('repassword')
            if password == repassword:
                register_data = forms.Register(request.POST)
                if register_data.is_valid():
                    data_clean = register_data.cleaned_data
                    clean_email = data_clean.get('email')
                    user = models.BuyerUser.objects.filter(email=clean_email).first()
                    if not user:
                        new_user = models.BuyerUser()
                        new_user.email = clean_email
                        clean_password = data_clean.get('password')
                        new_user.password = set_pwd(clean_password)
                        new_user.username = data_clean.get('username')
                        new_user.save()
                        return redirect('/buyer/login/')
                    else:
                        err_msg = '邮箱已被注册，请登录'
                else:
                    err_msg = '注册信息不完整'
            else:
                err_msg = "密码不一致"
        else:
            err_msg = '邮箱不能为空'

    return render(request, 'buyer/register.html', locals())


def login(request):
    err_msg = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        login_user = models.BuyerUser.objects.filter(username=username).first()
        if login_user:
            db_password = login_user.password
            password = set_pwd(request.POST.get('password'))
            if password == db_password:
                response_obj = redirect('/buyer/index/')
                response_obj.set_cookie('buyer_username', value=login_user.username)
                response_obj.set_cookie('buyer_user_id', value=login_user.id)
                response_obj.set_cookie('buyer_user_email', value=login_user.email)
                request.session['buyer_user_email'] = login_user.email
                return response_obj
            else:
                err_msg = "两次输入密码不一致"
        else:
            err_msg = "用户名不存在"

    return render(request, 'buyer/login.html', locals())


def logout(request):
    url = request.META.get('HTTP_REFERER', '/')
    response_obj = redirect(url)
    response_obj.delete_cookie('buyer_username')
    response_obj.delete_cookie('buyer_user_email')
    del request.session['buyer_user_email']
    return response_obj


def index(request):
    buyer_user_id = request.COOKIES.get('buyer_user_id')
    if buyer_user_id:
        buyer_user = models.BuyerUser.objects.get(id=int(buyer_user_id))
    goods_type = GoodsType.objects.all()
    result = []
    for gt in goods_type:
        goods = gt.goods_set.order_by('-goods_pro_time')
        if len(goods) >= 4:
            goods_list = goods[:4]
            result.append({
                'gt': gt,
                'goods_list': goods_list
            })

    return render(request, 'buyer/index.html', locals())


def goods_list(request):
    ty = request.GET.get('ty')
    kw = request.GET.get('kw')
    goods_display = []
    if ty == 't':
        gt = GoodsType.objects.get(id=int(kw))
        goods_display = gt.goods_set.order_by('-goods_pro_time')
    elif ty == 'k':
        goods_display = Goods.objects.filter(goods_name__contains=kw).order_by('-goods_pro_time')

    return render(request, 'buyer/goodslist.html', locals())


def goods_detail(request, idn):
    goods = Goods.objects.get(id=int(idn))
    return render(request, 'buyer/goodsdetail.html', locals())


@login_valid
def buyer_add_goods(request):
    buyer_user_id = int(request.COOKIES.get('buyer_user_id'))
    goods_id = request.GET.get('goods_id')
    count = request.GET.get('count')
    if goods_id and count:
        buy_user = models.BuyerUser.objects.get(id=int(buyer_user_id))
        buy_user_cart = buy_user.cartone_set.filter(status=1)
        for g in buy_user_cart:
            if g.goods.id == int(goods_id):
                g.count += int(count)
                g.save()
                break
        else:
            goods = Goods.objects.get(id=int(goods_id))
            new_add_cart = models.CartOne()
            new_add_cart.buy_user = buy_user
            new_add_cart.goods = goods
            new_add_cart.count = int(count)
            new_add_cart.save()

    url = request.META.get('HTTP_REFERER', '/')
    return redirect(url)


@login_valid
def ajax_buyer_add_goods(request):
    result = {
        'code': 200,
        'data': '',
    }
    if request.method == 'POST':
        buyer_user_id = int(request.COOKIES.get('buyer_user_id'))
        goods_id = request.POST.get('goods_id')
        count = request.POST.get('count', 1)
        buy_user = models.BuyerUser.objects.get(id=int(buyer_user_id))
        buy_user_cart = buy_user.cartone_set.filter(status=1)
        for g in buy_user_cart:
            if g.goods.id == int(goods_id):
                g.count += int(count)
                goods = Goods.objects.get(id=int(goods_id))
                if g.count > goods.goods_count:
                    g.count = goods.goods_count
                    result['data'] += '修改添加商品数量为该商品库存量'
                g.total_price = round(goods.goods_price * g.count, 2)
                g.save()
                break
        else:
            goods = Goods.objects.get(id=int(goods_id))
            new_add_cart = models.CartOne()
            new_add_cart.buy_user = buy_user
            new_add_cart.goods = goods
            new_add_cart.count = int(count)
            new_add_cart.total_price = round(goods.goods_price * new_add_cart.count, 2)
            new_add_cart.save()
        result['data'] += "加入购物车成功"
    else:
        result['code'] = 500
        result['data'] += "加入购物车失败"
    return JsonResponse(result)


@login_valid
def ajax_add_reduce(request):
    result = {
        'code': 200,
        'data': '',
    }
    buyer_user_id = int(request.COOKIES.get('buyer_user_id'))
    goods_id = int(request.GET.get('goods_id'))
    count = int(request.GET.get('count'))
    buy_user = models.BuyerUser.objects.get(id=int(buyer_user_id))
    cartone_obj = buy_user.cartone_set.get(goods_id=goods_id)
    if count <= 0:
        count = 0
    elif count >= cartone_obj.goods.goods_count:
        count = cartone_obj.goods.goods_count
    cartone_obj.count = count
    cartone_obj.total_price = cartone_obj.goods.goods_price * count
    cartone_obj.save()
    result['data'] = '商品数量修改成功'
    return JsonResponse(result)


@login_valid
def personal_cart(request):
    buyer_user_id = int(request.COOKIES.get('buyer_user_id'))
    buy_user = models.BuyerUser.objects.get(id=int(buyer_user_id))
    cart_goods = buy_user.cartone_set.filter(status=1, count__gte=1).order_by('-date')
    count = len(cart_goods)

    return render(request, 'buyer/personalcart.html', locals())


@login_valid
def buyer_user_info(request):
    return render(request, 'buyer/buyeruserinfo.html', locals())


@login_valid
def buyer_user_all_order(request,page=1):
    page = int(page)
    page_size = 6
    buyer_user_id = int(request.COOKIES.get('buyer_user_id'))
    buyer_user = models.BuyerUser.objects.get(id=buyer_user_id)
    orders = buyer_user.order_set.all().order_by('-order_date')
    orders_page = Paginator(orders, page_size)
    order_list = orders_page.page(page)
    page_range = list(orders_page.page_range)

    page_prev = page - 1  # 上一页
    page_next = page + 1  # 下一页
    if page_prev < 1:
        page_prev = 1
    if page_next > orders_page.num_pages:  # 总页数
        page_next = orders_page.num_pages

    return render(request, 'buyer/buyerallorder.html', locals())


# 单个提交订单 和 购物车合并
@login_valid
def new_order_info(request):
    goods_info = []
    yun_fee = 6
    total_fee = 0
    buyer_user_id = int(request.COOKIES.get('buyer_user_id'))
    request_data = request.GET
    goods_id = request_data.get('goods_id')
    count = request_data.get('count')
    if goods_id and count:
        goods_info.append((int(goods_id), int(count)))
    for k, v in request_data.items():
        if k.startswith('check_'):
            goods_id = k.rsplit('_', 1)[1]
            count = request_data.get('count_' + goods_id)
            goods_info.append((int(goods_id), int(count)))
    if request_data:
        new_order = models.Order()
        new_order.order_num = time.strftime('%Y%m%d%H%M%S') + random_str()
        new_order.order_user = models.BuyerUser.objects.get(id=buyer_user_id)
        new_order.save()

        for goods_id, count in goods_info:
            goods = Goods.objects.get(id=int(goods_id))
            new_order_info = models.OrderInfo()

            new_order_info.order_id = new_order
            new_order_info.store_id = goods.goods_store
            new_order_info.goods_id = int(goods_id)
            new_order_info.goods_name = goods.goods_name
            new_order_info.goods_picture = goods.goods_picture
            new_order_info.goods_count = int(count)
            new_order_info.goods_price = goods.goods_price
            new_order_info.goods_total_price = round(goods.goods_price * int(count), 2)
            new_order_info.save()
            total_fee += new_order_info.goods_total_price
        new_order.order_total = round(total_fee, 2)
        new_order.save()
        total_fee += yun_fee
        total_fee = round(total_fee, 2)
    return render(request, 'buyer/orderinfo.html', locals())


@login_valid
def ali_pay(request):
    order_num = request.GET.get('order_num')
    total_fee = request.GET.get('total_fee')
    subject = request.GET.get('subject')
    # 实例化支付
    ali_pay = AliPay(
        appid="2016101200667842",
        app_notify_url=None,
        alipay_public_key_string=ALIPAY_PUBLIC,
        app_private_key_string=APP_PRIVATE,
        sign_type="RSA2"
    )

    # 实例化订单
    order_string = ali_pay.api_alipay_trade_page_pay(
        out_trade_no=order_num,
        total_amount=str(total_fee),
        subject=subject,
        return_url='http://127.0.0.1:8080/buyer/payinfo/',
        notify_url=None
    )
    ret = ALIPAY_URL + '?' + order_string
    return redirect(ret)


@login_valid
def pay_info(request):
    order_num = request.GET.get('out_trade_no')
    if order_num:
        order = models.Order.objects.get(order_num=order_num)
        order.order_status = 1
        order.save()
        order.orderinfo_set.all().update(status=1)
    return render(request, 'buyer/payinfo.html', locals())
