import time
import json
import random
import hashlib
import requests
import datetime

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.db.models import Avg, Sum, Min, Max, Count, F, Q

from Seller import models, forms
from Qshop.settings import DING_URL


def set_pwd(password):
    SALT = b'bestwish'
    md5 = hashlib.md5(SALT)
    md5.update(password.encode('utf-8'))
    ret = md5.hexdigest()
    return ret


def login_valid(func):
    def inner(request, *args, **kwargs):
        cookie_email = request.COOKIES.get('seller_user_email')
        session_email = request.session.get('seller_user_email')
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
    print(request.session.get('seller_user_email'))
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
                    # 验证码校验
                    code_obj = models.ValidCode.objects.filter(code_user=email, code_state=0)\
                        .order_by('-code_datetime').first()
                    dif_time = time.time() - code_obj.code_datetime.timestamp()
                    if valid_code.upper() == code_obj.code_content.upper() and dif_time <= 300:
                        code_obj.code_state = 1
                        code_obj.save()
                        response_obj = redirect('/seller/index/')
                        response_obj.set_cookie('seller_user_email', value=user.email)
                        response_obj.set_cookie('seller_username', value=user.username)
                        response_obj.set_cookie('seller_user_id', value=user.id)
                        request.session['seller_user_email'] = user.email
                        return response_obj
                    else:
                        err_msg = '验证码错误'
                else:
                    err_msg = '密码错误'
            else:
                err_msg = '邮箱未注册，请先注册'
        else:
            err_msg = '邮箱不能为空，请重新输入'
    return render(request, 'seller/login.html', locals())


@login_valid
def index(request):
    seller_user_id = request.COOKIES.get('seller_user_id')
    seller_user = models.SellerUser.objects.get(id=int(seller_user_id))

    return render(request, 'seller/index.html', locals())


def create_string():
    string = [str(i) for i in range(10)]
    upper_string = [chr(i) for i in range(65, 91)]
    lower_string = [chr(i) for i in range(97, 123)]
    string.extend(upper_string)
    string.extend(lower_string)
    string = ''.join(string)
    return string


def create_valid_code(code_length=6):
    valid_code = ''
    for i in range(code_length):
        valid_code += random.choice(create_string())
    return valid_code


def send_ding(content, to=None):
    headers = {
        "Content-Type": "application/json",
        "Charset": "utf-8"
    }
    requests_data = {
        "msgtype": "text",
        "text": {
            "content": content
        },
        "at": {
            "atMobiles": [
            ],
            "isAtAll": True
        }
    }
    if to:
        requests_data["at"]["atMobiles"].append(to)
        requests_data["at"]["isAtAll"] = False
    else:
        requests_data["at"]["atMobiles"].clear()
    sendData = json.dumps(requests_data)
    response = requests.post(url=DING_URL, headers=headers, data=sendData)
    content = response.json()
    return content


# 通过钉钉机器人给钉钉聊天群发短信
def send_login_code(request):
    result = {
        'code': 200,
        'data': '',
    }
    if request.method == 'POST':
        email = request.POST.get('email')
        valid_code = create_valid_code()
        new_code = models.ValidCode()
        new_code.code_user = email
        new_code.code_content = valid_code
        new_code.save()
        send_data = "【安利巴巴】验证码：{}。您正在使用登录功能，该验证码用于身份验证，请勿泄露。" \
            .format(new_code.code_content)
        send_ding(send_data, to=email)
        result['data'] = "验证码发送成功。"
    else:
        result['code'] = 403
        result['data'] = "请求错误！"

    return JsonResponse(result)