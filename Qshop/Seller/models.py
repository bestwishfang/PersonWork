from django.db import models


# Create your models here.
class SellerUser(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=32)

    username = models.CharField(max_length=32, null=True, blank=True)
    phone_number = models.CharField(max_length=32, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=32, null=True, blank=True)
    photo = models.ImageField(upload_to='seller/images', null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    user_type = models.IntegerField(default=1)  # 0 买家 1 卖家 2 管理者


class ValidCode(models.Model):
    code_content = models.CharField(max_length=32)
    code_user = models.CharField(max_length=32)
    code_datetime = models.DateTimeField(auto_now=True)
    code_state = models.IntegerField(default=0)  # 0 表示未使用 1 已使用

