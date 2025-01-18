from django.urls import path
from backend.views import LoginView


"""
Urlpatterns for backend api
Урлпаттерны для api приложения backend
"""
app_name = 'backend'
urlpatterns = [
    path('login', LoginView.as_view(), name='login')
    ]
