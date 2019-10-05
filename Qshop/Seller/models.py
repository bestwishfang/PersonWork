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


class Goods(models.Model):
    goods_num = models.CharField(max_length=10)
    goods_name = models.CharField(max_length=32)
    goods_price = models.FloatField()
    goods_count = models.IntegerField()
    goods_location = models.CharField(max_length=254)
    goods_safe_date = models.IntegerField()
    goods_pro_time = models.DateField()
    goods_picture = models.ImageField(upload_to='seller/images')
    goods_status = models.IntegerField(default=1)  # 商品状态 0 表示下架  1 表示在售
    goods_description = models.TextField(default="新鲜食品，好味道")

    goods_type = models.ForeignKey(to='GoodsType', on_delete=models.CASCADE)
    goods_store = models.ForeignKey(to='SellerUser', on_delete=models.CASCADE)  # 一个商品 对应 一个商店（卖家）

    class Meta:
        verbose_name = "商品"


class GoodsType(models.Model):
    label = models.CharField(max_length=32)
    description = models.TextField(null=True, blank=True)
    picture = models.ImageField(upload_to='seller/images')

