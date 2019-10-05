import time
import hashlib

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse

from Buyer import models, forms


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

    return render(request, 'buyer/index.html', locals())
