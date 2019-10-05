from django.urls import path, re_path
from Buyer import views

urlpatterns = [
    path('register/', views.register),
    path('login/', views.login),
    path('logout/', views.logout),
    path('index/', views.index),

]