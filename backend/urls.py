from django.urls import path, include
from rest_framework.routers import DefaultRouter
from backend.views import LoginView, RegisterAccountView, ConfirmEmailView, ProductInfoView, BasketViewSet


app_name = 'backend'
router = DefaultRouter()
router.register(r'basket', BasketViewSet, basename='basket')
"""
Urlpatterns for backend api
Урлпаттерны для api приложения backend
"""
urlpatterns = [
    path('user/login', LoginView.as_view(), name='login'),
    path('user/register', RegisterAccountView.as_view(), name='user-register'),
    path('confirm-email/<int:user_id>/', ConfirmEmailView.as_view(), name='confirm-email'),
    path('products/', ProductInfoView.as_view(), name='product-list'),
    path('', include(router.urls)), # Add route for basketviewset, добавляем роуты для basketviewset
    ]
