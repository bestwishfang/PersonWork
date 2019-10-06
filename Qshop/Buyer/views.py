import time
import hashlib

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse

from Buyer import models, forms
from Seller.models import GoodsType, Goods


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


