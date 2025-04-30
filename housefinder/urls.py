from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('register/', views.register, name='register'),
    path('main_menu/', views.main_menu, name='main_menu'),
    path('find_houses/', views.find_houses, name='find_houses'), 
    path('predict_price/', views.predict_price, name='predict_price'),
]