from django.urls import path, re_path
from Seller import views

urlpatterns = [
    path('register/', views.register),
    path('login/', views.login),
    path('slc/', views.send_login_code),
    path('index/', views.index),
    re_path(r'^$', views.index),

    path('personal/', views.personal_info),

    path('goods/', views.goods_list),
    path('goodsadd/', views.goods_add),
    re_path(r'goods/operation/(?P<status>[01])/(?P<ids>\d+)/', views.goods_operate),
    re_path(r'^goods/(?P<status>[01])/(?P<page>\d+)/', views.goods_list),

]