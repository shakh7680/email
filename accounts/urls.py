
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register', views.register_attempt, name="register_attempt"),   
    path('login', views.login_attempt, name="login_attempt"),
    path('token', views.token_send, name="token_send"),
    path('success', views.success, name="success"),
    path('verify/<auth_token>', views.verify, name="verify"),
    path('error', views.error, name="error"),
    path('logout', views.logout, name="logout"),
    path('reset_password_send_email', views.reset_pass_send_email, name='reset_pass_send_email'),
    path('reset_password/<get_token>', views.reset_password, name='reset_password'),
    path('reset_password_form/<get_token>', views.reset_password_form, name="reset_password_form"),
]
