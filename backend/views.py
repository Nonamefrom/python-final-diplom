from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from django.db.models import Q, F, Sum
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import action
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.viewsets import ViewSet

from backend.serializers import (LoginSerializer, RegisterAccountSerializer, ProductInfoSerializer,
                                 OrderSerializer, OrderedItemSerializer)
from backend.models import ProductInfo, Order, OrderedItem


class LoginView(APIView):
    """
    Class and post method for authenticate user, find user in table, get his name and use it for auth
    Класс и функиця  POST авторизации, проверяет есть ли текущий меил в БД, берет имя юзера и авторизует
    с ним пользователя
    variables(поля): email, password
    """
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            # Сheck mail in DB, Проверяет есть ли юзер с данным email в БД
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

            # Get username and authcheck, берет имя юзера и производит попытку авторизации
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    "message": "Login successful",
                    "token": token.key
                }, status=status.HTTP_200_OK)
            return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterAccountView(APIView):
    """
    Class and post method for registering users.
    Checks if email exists in DB, saves user, and sends confirmation email or prints the confirmation link.
    Variables(fields): name, surname, email, password
    Responce: status code and message if all variables are valid, status code and message
    """
    def post(self, request):
        serializer = RegisterAccountSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Save the user
                user = serializer.save()

                # Generate email confirmation link
                confirmation_link = request.build_absolute_uri(
                    reverse('backend:confirm-email', kwargs={'user_id': user.id})
                )

                # Print confirmation link for local debugging
                print(f"Confirmation link for local debugging: {confirmation_link}")

                # Uncomment the following lines for actual email sending
                # send_mail(
                #     'Confirm Your Registration',
                #     f'Click the link to confirm your registration: {confirmation_link}',
                #     settings.DEFAULT_FROM_EMAIL,
                #     [user.email],
                # )

                return Response(
                    {"message": "User registered successfully. Please confirm your email."},
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                # Log the error and return a 500 response
                print(f"Error during registration: {e}")
                return Response(
                    {"error": "An unexpected error occurred. Please try again later."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfirmEmailView(APIView):
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        if user.is_active:
            return Response({"message": "Email is already confirmed."}, status=status.HTTP_200_OK)

        user.is_active = True
        user.save()
        return Response({"message": "Email confirmed successfully."}, status=status.HTTP_200_OK)


class ProductInfoView(APIView):
    """
    A class for searching products view, based on the specified filters with get parameters
    Класс для поиска продуктов с фильтрацией в гет-параметрах
    Methods:
    - get: Retrieve the product information based on the specified filters.
    Получение информации о продукте, возможно использование фильтров
    Parameters examples(примеры параметров): ?shop_id=1 ?category_id=2 ?search=Smartphone ?min_price=500&max_price=1000
    """

    def get(self, request: Request, *args, **kwargs):
        query = Q(shop__state=True)

        shop_id = request.query_params.get('shop_id')
        category_id = request.query_params.get('category_id')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        search = request.query_params.get('search')

        if shop_id:
            query &= Q(shop_id=shop_id)

        if category_id:
            query &= Q(product__category_id=category_id)

        if min_price:
            query &= Q(price__gte=min_price)

        if max_price:
            query &= Q(price__lte=max_price)

        if search:
            query &= Q(
                Q(product__name__icontains=search) |
                Q(model__icontains=search) |
                Q(shop__name__icontains=search)
            )

        queryset = ProductInfo.objects.filter(query).select_related(
            'shop', 'product__category'
        ).prefetch_related(
            'product_parameters__parameter'
        ).distinct()

        serializer = ProductInfoSerializer(queryset, many=True)
        return Response(serializer.data)


class BasketViewSet(ViewSet):
    """
    A viewset for managing the user's shopping basket.

    Methods:
    - list (GET): Retrieve the items in the user's basket.
    - create (POST): Add an item to the user's basket.
    - update (PUT): Update the quantity of an item in the user's basket.
    - destroy (DELETE): Remove all items from the user's basket or a specific item if provided.
    """

    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def list(self, request, *args, **kwargs):
        user_orders = Order.objects.filter(user=request.user, status='basket')
        serializer = OrderSerializer(user_orders, many=True)
        return Response(serializer.data)

    def create(self, request):
        product_info_id = request.data.get('product_info_id')
        quantity = request.data.get('quantity', 1)

        if not product_info_id:
            return Response({'Status': False, 'Error': 'Product info ID is required'}, status=400)

        product_info = get_object_or_404(ProductInfo, id=product_info_id)

        order, _ = Order.objects.get_or_create(user=request.user, status='basket')
        shop = product_info.shop  # или другой способ получить shop, если он связан с product_info
        ordered_item, created = OrderedItem.objects.get_or_create(
            order=order,
            product_info=product_info,
            shop=shop,  # передаем shop_id
            defaults={'quantity': quantity}
        )
        if not created:
            ordered_item.quantity += int(quantity)
            ordered_item.save()

        return Response({'Status': True, 'Message': 'Item added to basket'})

    def update(self, request, pk=None):
        quantity = request.data.get('quantity')

        if not quantity:
            return Response({'Status': False, 'Error': 'Quantity is required'}, status=400)

        ordered_item = get_object_or_404(OrderedItem, id=pk, order__user=request.user, order__status='basket')
        ordered_item.quantity = quantity
        ordered_item.save()

        return Response({'Status': True, 'Message': 'Item quantity updated'})

    def destroy(self, request, pk=None):
        if pk:
            ordered_item = get_object_or_404(OrderedItem, id=pk, order__user=request.user, order__status='basket')
            ordered_item.delete()
            return Response({'Status': True, 'Message': 'Item removed from basket'})
        else:
            Order.objects.filter(user=request.user, state='basket').delete()
            return Response({'Status': True, 'Message': 'Basket cleared'})
