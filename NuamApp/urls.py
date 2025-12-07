from django.urls import path
from django.contrib.auth import views as auth_views
from .forms import LoginForm
from . import views

urlpatterns = [
    path('', views.main, name = "main"),
    path('login/', auth_views.LoginView.as_view(
        template_name = 'login.html',
        authentication_form = LoginForm,
    ), name = "login"),
    path('home-redirect/', views.redireccion_login, name = 'redireccion_login'),
    path('register/', views.register, name = "register"),
    path('holder/', views.holder, name = "holder"),
    path('client/create/', views.create_client, name='create_client'),
    path('client/modify/<int:cliente_id>/', views.modify_client, name="modify_client"),
    path('client/delete/<int:cliente_id>/', views.delete_client, name='delete_client'),
    path('admin-panel/', views.admin_dashboard, name = 'admin_dashboard'),
    path('admin-panel/carga-masiva/', views.carga_masiva_clasificaciones, name = 'carga_masiva'),
    path('admin-panel/crear-emisor/', views.create_emisor, name = 'create_emisor'),
    path('admin-panel/toggle-usuario/<int:user_id>/', views.toggle_status_corredor, name = 'toggle_status_corredor'),
    path('admin-panel/delete-client-global/<int:cliente_id>/', views.delete_any_client, name = 'delete_any_client')
]