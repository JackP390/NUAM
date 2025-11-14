from django.urls import path
from django.contrib.auth import views as auth_views
from .forms import LoginForm
from . import views

urlpatterns = [
    path('', views.main, name = "main"),
    path('login/', auth_views.LoginView.as_view(
        template_name = 'login.html',
        authentication_form = LoginForm,
        next_page = 'holder'
    ), name = "login"),
    path('register/', views.register, name = "register"),
    path('holder/', views.holder, name = "holder")
]