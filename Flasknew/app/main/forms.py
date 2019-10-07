import wtforms
from flask_wtf import FlaskForm
from wtforms import validators

from wtforms import ValidationError


def keywords_valid(form, field):
    """
    :param form: 表单
    :param field:  字段
    这两个都不用主动传参
    """
    data = field.data  # 获取input内容（value）
    keywords = ["admin", "GM", "管理员", "版主"]
    if data in keywords:
        raise ValidationError("不可以以敏感词命名")


class TaskForm(FlaskForm):
    name = wtforms.StringField(label="name",
                               render_kw={
                                   "class": "form-control",
                                   "placeholder": "任务名称"
                               },
                               validators=[
                                   validators.DataRequired("姓名不可以为空"),
                                   # validators.length(max=8,min=6), #6-8位
                                   keywords_valid
                                   # validators.Email("必须符合邮箱格式"),
                               ]
                               )
    description = wtforms.TextField(
        label="description",
        render_kw={
            "class": "form-control",
            "placeholder": "任务描述"
        },
        validators=[
            validators.EqualTo("name")  # name和description的内容是否一样
        ]
    )
    time = wtforms.DateField(
        label="time",
        render_kw={
            "class": "form-control",
            "placeholder": "任务时间"
        }
    )
    public = wtforms.StringField(
        label="public",
        render_kw={
            "class": "form-control",
            "placeholder": "公布任务人"
        }
    )
