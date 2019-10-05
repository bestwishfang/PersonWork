from django.urls import path, re_path
from Seller import views

urlpatterns = [
    path('register/', views.register),
    path('login/', views.login),
    path('slc/', views.send_login_code),
    path('index/', views.index),
    re_path(r'^$', views.index),

]