from django.urls import path
from backend.views import LoginView, RegisterAccountView, ConfirmEmailView


app_name = 'backend'
"""
Urlpatterns for backend api
Урлпаттерны для api приложения backend
"""
urlpatterns = [
    path('user/login', LoginView.as_view(), name='login'),
    path('user/register', RegisterAccountView.as_view(), name='user-register'),
    path('confirm-email/<int:user_id>/', ConfirmEmailView.as_view(), name='confirm-email'),
    ]
