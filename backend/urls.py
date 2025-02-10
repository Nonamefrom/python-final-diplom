from django.urls import path, include
from rest_framework.routers import DefaultRouter
from backend.views import (LoginView, RegisterAccountView, ConfirmEmailView, ProductInfoView, BasketViewSet,
                           ContactViewSet, OrderViewSet, UserProfileViewSet, ProductImageViewSet)


app_name = 'backend'
router = DefaultRouter()
router.register(r'basket', BasketViewSet, basename='basket') # Route for basketApi, роут для корзины
router.register(r'contacts', ContactViewSet, basename='contact') # Route for contactApi, роут для контактов
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'user', UserProfileViewSet, basename='user')
router.register(r'products', ProductImageViewSet, basename='product-image')

"""
Urlpatterns for backend api
Урлпаттерны для api приложения backend
"""
urlpatterns = [
    path('user/login', LoginView.as_view(), name='login'),
    path('user/register', RegisterAccountView.as_view(), name='user-register'),
    path('confirm-email/<int:user_id>/', ConfirmEmailView.as_view(), name='confirm-email'),
    path('products/', ProductInfoView.as_view(), name='product-list'),
    path('', include(router.urls)), # Add route for viewset, добавляем роуты для viewset
    ]
