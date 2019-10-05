import time
import hashlib
import datetime

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.db.models import Avg, Sum, Min, Max, Count, F, Q

from Seller import models, forms


def set_pwd(password):
    SALT = b'bestwish'
    md5 = hashlib.md5(SALT)
    md5.update(password.encode('utf-8'))
    ret = md5.hexdigest()
    return ret


def login_valid(func):
    def inner(request, *args, **kwargs):
        cookie_email = request.COOKIES.get('user_email')
        session_email = request.session.get('user_email')
        if cookie_email and cookie_email == session_email:
            return func(request, *args, **kwargs)
        else:
            return redirect('/seller/login/')

    return inner


# Create your views here.

def register(request):
    err_msg = ''
    if request.method == 'POST':
        print(request.FILES)
        email = request.POST.get('email')
        photo = request.FILES.get('photo')
        if email:
            password = request.POST.get('password')
            repassword = request.POST.get('repassword')
            if password == repassword:
                register_data = forms.Register(request.POST)
                if register_data.is_valid():
                    data_clean = register_data.cleaned_data
                    clean_email = data_clean.get('email')
                    user = models.SellerUser.objects.filter(email=clean_email).first()
                    if not user:
                        new_user = models.SellerUser()
                        new_user.email = clean_email
                        clean_password = data_clean.get('password')
                        new_user.password = set_pwd(clean_password)
                        new_user.username = data_clean.get('username')
                        new_user.phone_number = data_clean.get('phone_number')
                        new_user.gender = data_clean.get('gender')
                        new_user.age = data_clean.get('age')
                        new_user.photo = photo
                        new_user.address = request.POST.get('address')
                        new_user.save()
                        return redirect('/seller/login/')
                    else:
                        err_msg = '邮箱已被注册，请登录'
                else:
                    err_msg = '注册信息不完整'
            else:
                err_msg = "密码不一致"
        else:
            err_msg = '邮箱不能为空'
    return render(request, 'seller/register.html', locals())


def login(request):
    print(request.COOKIES)
    print(request.session.get('user_email'))
    err_msg = ''
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        valid_code = request.POST.get('validCode')
        if email:
            user = models.SellerUser.objects.filter(email=email).first()
            if user:
                password = set_pwd(password)
                if password == user.password:
                    response_obj = redirect('/seller/index/')
                    response_obj.set_cookie('user_email', value=user.email)
                    response_obj.set_cookie('username', value=user.username)
                    response_obj.set_cookie('user_id', value=user.id)
                    request.session['user_email'] = user.email
                    return response_obj
                else:
                    err_msg = '验证码错误'

            else:
                err_msg = '邮箱未注册，请先注册'
        else:
            err_msg = '邮箱不能为空，请重新输入'
    return render(request, 'seller/login.html', locals())


@login_valid
def index(request):
    user_id = request.COOKIES.get('user_id')
    seller_user = models.SellerUser.objects.get(id=int(user_id))
    return render(request, 'seller/index.html', locals())
