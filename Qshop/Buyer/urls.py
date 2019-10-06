from django.urls import path, re_path
from Buyer import views

urlpatterns = [
    path('register/', views.register),
    path('login/', views.login),
    path('logout/', views.logout),
    path('index/', views.index),
    path('goodslist/', views.goods_list),
    re_path(r'goodsdetail/(?P<idn>\d+)/', views.goods_detail),

    path('personalcart/', views.personal_cart),
    path('addgoods/', views.buyer_add_goods),

    path('ajaxaddreduce/', views.ajax_add_reduce),
    path('ajaxaddgoods/', views.ajax_buyer_add_goods),

]