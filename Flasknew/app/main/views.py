import hashlib
import functools

from flask import request
from flask import session
from flask import render_template, redirect

from . import main
from app.models import *


def set_pwd(password):
    SALT = b'bestwish'
    md5 = hashlib.md5(SALT)
    md5.update(password.encode('utf-8'))
    ret = md5.hexdigest()
    return ret


class Pager:
    """
    flask分页通过sqlalachemy查询进行分页
    offset 偏移，开始查询的位置
    limit 单页条数
    分页器需要具备的功能
    页码
    分页数据
    是否第一页
    是否最后一页
    """

    def __init__(self, data, page_size):
        """

        :param data: 要分页的数据
        :param page_size: 每页多少条
        """
        self.data = data  # 总数据
        self.page_size = page_size  # 单页数据
        self.is_start = False
        self.is_end = False
        self.page_count = len(data)
        self.next_page = 0  # 下一页
        self.previous_page = 0  # 上一页
        self.page_nmuber = self.page_count / page_size
        # (data+page_size-1)//page_size
        if self.page_nmuber == int(self.page_nmuber):
            self.page_nmuber = int(self.page_nmuber)
        else:
            self.page_nmuber = int(self.page_nmuber) + 1

        self.page_range = range(1, self.page_nmuber + 1)  # 页码范围

    def page_data(self, page):
        """
        返回分页数据
        :param page: 页码
        page_size = 10
        1    offect 0  limit(10)
        2    offect 10 limit(10)
        page_size = 10
        1     start 0   end  10
        2     start 10   end  20
        3     start 20   end  30
        """
        self.next_page = int(page) + 1
        self.previous_page = int(page) - 1
        if page <= self.page_range[-1]:
            page_start = (page - 1) * self.page_size
            page_end = page * self.page_size
            # data = self.data.offset(page_start).limit(self.page_size)
            data = self.data[page_start:page_end]
            if page == 1:
                self.is_start = True
            else:
                self.is_start = False
            if page == self.page_range[-1]:
                self.is_end = True
            else:
                self.is_end = False
        else:
            data = ["没有数据"]
        return data


def login_valid(func):
    @functools.wraps(func)  # 保留原函数的名称
    def inner(*args, **kwargs):
        username = request.cookies.get("username")
        id = request.cookies.get("id", "0")
        user = User.query.get(int(id))
        session_username = session.get("username")
        if user:  # 检测是否有对应id的用户
            if user.user_name == username and username == session_username:  # 用户名是否对应
                return func(*args, **kwargs)
            else:
                return redirect("/login/")
        else:
            return redirect("/login/")

    return inner


@main.route("/register/", methods=["GET", "POST"])
def register():
    """
    form表单提交的数据由request.form接受
    """
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        user = User()
        user.user_name = username
        user.password = set_pwd(password)
        user.email = email
        user.save()
    return render_template("register.html")


@main.route("/login/", methods=["get", "post"])
def login():
    error = ""
    if request.method == "POST":
        form_data = request.form
        email = form_data.get("email")
        password = form_data.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            db_password = user.password
            if set_pwd(password) == db_password:
                response = redirect("/index/")
                response.set_cookie("username", user.user_name)
                response.set_cookie("email", user.email)
                response.set_cookie("id", str(user.id))
                session["username"] = user.user_name
                return response
            else:
                error = "密码错误"
        else:
            error = "用户名不存在"
    return render_template("login.html", error=error)


@main.route("/logout/")
def logout():
    response = redirect("/login/")
    response.delete_cookie("username")
    response.delete_cookie("email")
    response.delete_cookie("id")
    session.pop("username")
    del session["username"]
    return response


@main.route("/")
@login_valid
def index():
    name = 'fang'
    return render_template("index.html", **locals())


@app.route("/holiday_leave/", methods=["GET", "POST"])
# @csrf.exempt
def holiday_leave():
    if request.method == "POST":
        data = request.form
        request_user = data.get("request_user")
        request_type = data.get("request_type")
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        phone = data.get("phone")
        request_description = data.get("request_description")

        leave = Leave()
        leave.request_id = request.cookies.get("id")
        leave.request_name = request_user
        leave.request_type = request_type  # 假期类型
        leave.request_start_time = start_time  # 起始时间
        leave.request_end_time = end_time  # 结束时间
        leave.request_description = request_description  # 请假事由
        leave.request_phone = phone  # 联系方式
        leave.request_status = "0"  # 假条状态
        leave.save()
        return redirect("/leave_list/1/")
    return render_template("holiday_leave.html")


@main.route("/leave_list/<int:page>/")
@login_valid
def leave_list(page):
    leaves = Leave.query.all()
    pager = Pager(leaves, 2)
    page_data = pager.page_data(page)
    return render_template("leave_list.html", **locals())
