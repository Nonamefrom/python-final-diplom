import requests
from django.core.files.base import ContentFile
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status, viewsets
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
from .tasks import send_order_confirmation_email, process_user_avatar, process_product_image

from backend.serializers import (LoginSerializer, RegisterAccountSerializer, ProductInfoSerializer,
                                 OrderSerializer, OrderConfirmSerializer, OrderListSerializer, ContactSerializer,
                                 )
from backend.models import ProductInfo, Order, OrderedItem, Contact, UserProfile, ProductImage
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


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
    Класс и post  запрос для регистрации пользователей
    Checks if email exists in DB, saves user, and sends confirmation email.
    Проверяет наличие мейл в БД и сохраняет юзера и отправляет письмо с подтверждением
    Variables(fields) входящие переменные(поля): name, surname, email, password
    Responce: status code and message if all variables are valid, status code and message
    В ответе статус код и сообщение если все поля валидны
    """
    def post(self, request):
        serializer = RegisterAccountSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Save the user, сохраняем пользователя
                user = serializer.save()

                # Generate email confirmation link, генерируем ссылку подтверждение
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
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

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
    Набор для управления пользовательской корзиной.
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


class ContactViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user contacts.
    ViewSet для управления контактами пользователя.
    Предоставляет методы:
        - GET: Get list of contacts for this user. Получение списка контактов или информации о конкретном контакте.
        - POST: Add new contact. Добавление нового контакта.
        - PUT: Update existing contact. Обновление существующего контакта.
        - DELETE: Delete contact. Удаление контакта.
    """
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return contacts, filtered by the current user.
        Возвращает контакты, принадлежащие текущему пользователю.
        """
        return Contact.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Set the current user as the owner of the contact.
        Устанавливает текущего пользователя как владельца контакта.
        """
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """
        Return phone and address contacts for the user.
        Возвращает телефон и список адресов для пользователя.
        """
        user = request.user
        contacts = self.get_queryset()

        # Extract the phone, изымаем телефон
        phone = contacts.filter(phone__isnull=False).values_list('phone', flat=True).first()

        # Extract addresses, изымаем адреса
        addresses = contacts.filter(city__isnull=False, street__isnull=False)
        serializer = self.get_serializer(addresses, many=True)

        return Response({
            "phone": phone,
            "contacts": serializer.data
        })

class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user orders.
    ViewSet для управления заказами пользователя.
    """
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = OrderConfirmSerializer

    def get_queryset(self):
        """
        Returns orders for the current user, or all orders if the user is staff.
        Возвращает заказы. Обычным пользователям достыпны свои заказы,
        сотрудники (is_staff=True) могут видеть все заказы.
        """
        if self.request.user.is_staff:
            return Order.objects.all().select_related('contact').prefetch_related('orders_items__product_info')
        return Order.objects.filter(user=self.request.user).select_related('contact').prefetch_related(
            'orders_items__product_info')

    def get_serializer_class(self):
        """
        Use different serializers.
        - `OrderListSerializer` for search order's (list)
        - `OrderSerializer` for detail view order (retrieve)
        Использует разные сериализаторы:
        - `OrderListSerializer` для списка заказов (list)
        - `OrderSerializer` для детального просмотра заказа (retrieve)
        """
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer

    @action(detail=False, methods=['post'])
    def confirm_order(self, request):
        """
        Confirm order by basker id and contact id
        Подтверждение заказа по ID корзины и ID контакта.
        """
        serializer = OrderConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        basket_id = serializer.validated_data['basket_id']
        contact_id = serializer.validated_data['contact_id']

        order = get_object_or_404(Order, id=basket_id, user=request.user, status='basket')
        contact = get_object_or_404(Contact, id=contact_id, user=request.user)

        # Calculate common total order,Вычисляем общую сумму заказа
        total_price = sum(item.quantity * item.product_info.price for item in order.orders_items.all())

        # Refresh order, Обновляем заказ
        order.status = 'confirmed'
        order.contact = contact
        order.total_price = total_price
        order.save()

        send_order_confirmation_email.delay(order.id, request.user.email, total_price, contact.city, contact.street)

        return Response({"message": f"Заказ №{order.id} подтвержден, письмо отправляется!"})

        # Send mail to user, Отправляем email пользователю синхронно
        #send_mail(
            #subject="Подтверждение заказа",
            #message=f"Ваш заказ №{order.id} подтвержден! Сумма: {total_price} руб.\nАдрес доставки: {contact.city}, {contact.street}",
            #from_email="shop@example.com",
            #recipient_list=[request.user.email],
            #fail_silently=False,
        #)

        #return Response({"message": "Заказ подтвержден и email отправлен."}, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        """
        Update the status of the order.
        Обновление статусa заказа.
        """
        order = self.get_object()
        new_status = request.data.get('status')

        # Check exist status,Проверяем наличие статуса
        allowed_statuses = ['basket', 'processing', 'completed', 'canceled']
        if new_status not in allowed_statuses:
            return Response({"error": "Недопустимый статус"}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_staff and new_status in ['processing', 'completed', 'canceled']:
            return Response({"error": "Вы не можете менять статус заказа"}, status=status.HTTP_403_FORBIDDEN)

        order.status = new_status
        order.save()
        return Response({"status": "Обновлено", "new_status": order.status})


class UserProfileViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['post'])
    def foto_load(self, request):
        """Загрузка аватара (по ссылке или файлом)"""
        user = request.user
        user_profile, created = UserProfile.objects.get_or_create(user=user)  # Гарантируем, что профиль существует

        avatar_url = request.data.get('url')
        avatar_file = request.FILES.get('file')

        if avatar_url:
            response = requests.get(avatar_url)
            if response.status_code == 200:
                user_profile.avatar.save(f"{user.id}_avatar.jpg", ContentFile(response.content))
                process_user_avatar.delay(user_profile.avatar.name)  # Отправляем в Celery
                return Response({"message": "Аватар загружается в фоне"}, status=status.HTTP_200_OK)
            return Response({"error": "Не удалось загрузить изображение"}, status=status.HTTP_400_BAD_REQUEST)

        elif avatar_file:
            user_profile.avatar = avatar_file
            user_profile.save()
            process_user_avatar.delay(user_profile.avatar.name)  # Отправляем в Celery
            return Response({"message": "Аватар загружен и обрабатывается"}, status=status.HTTP_200_OK)

        return Response({"error": "Укажите URL или загрузите файл"}, status=status.HTTP_400_BAD_REQUEST)


class ProductImageViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['post'])
    def load_foto(self, request):
        """Загрузка изображения товара (по ссылке или файлом)"""
        product_info_id = request.data.get('product_info_id')
        product_info = get_object_or_404(ProductInfo, id=product_info_id)
        product = product_info.product  # Получаем связанный Product

        # Найти или создать ProductImage
        product_image, created = ProductImage.objects.get_or_create(product=product)

        image_url = request.data.get('url')
        image_file = request.FILES.get('file')

        if image_url:
            response = requests.get(image_url)
            if response.status_code == 200:
                product_image.image.save(f"product_{product.id}.jpg", ContentFile(response.content))
                process_product_image.delay(product_image.image.name)  # Отправляем в Celery
                return Response({"message": "Изображение загружается в фоне"}, status=status.HTTP_200_OK)
            return Response({"error": "Не удалось загрузить изображение"}, status=status.HTTP_400_BAD_REQUEST)

        elif image_file:
            product_image.image = image_file
            product_image.save()
            process_product_image.delay(product_image.image.name)  # Отправляем в Celery
            return Response({"message": "Изображение загружено и обрабатывается"}, status=status.HTTP_200_OK)

        return Response({"error": "Укажите URL или загрузите файл"}, status=status.HTTP_400_BAD_REQUEST)
