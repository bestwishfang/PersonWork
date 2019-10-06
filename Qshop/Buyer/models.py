from django.db import models
from Seller.models import SellerUser, Goods


# Create your models here.
class BuyerUser(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=32)

    username = models.CharField(max_length=32, null=True, blank=True)
    phone_number = models.CharField(max_length=32, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=32, null=True, blank=True)
    photo = models.ImageField(upload_to='buyer/images', null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    user_type = models.IntegerField(default=0)  # 0 买家 1 卖家 2 管理者


class CartOne(models.Model):
    """
    购物车
    """
    buy_user = models.ForeignKey(to='BuyerUser', on_delete=models.CASCADE)
    goods = models.ForeignKey(to=Goods, on_delete=models.CASCADE)
    goods_unit = models.CharField(max_length=32, default='500g')
    count = models.IntegerField()
    total_price = models.FloatField(null=True, blank=True)
    status = models.IntegerField(default=1)  # 1 表示存在 0 表示已删除
    date = models.DateTimeField(auto_now=True)
