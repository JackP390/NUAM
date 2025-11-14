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
    path('holder/', views.holder, name = "holder"),
    path('client/create/', views.create_client, name='create_client'),
    path('client/modify/<int:cliente_id>/', views.modify_client, name="modify_client"),
    path('client/delete/<int:cliente_id>/', views.delete_client, name='delete_client')
]