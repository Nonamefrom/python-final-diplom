from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError
from .models import Product, ProductParameter, ProductInfo, Order, OrderedItem, Contact


class LoginSerializer(serializers.Serializer):
    """
    Serializer for login post method.
    Сериалайзер для логина post method.
    """
    email = serializers.EmailField()
    password = serializers.CharField()


class RegisterAccountSerializer(serializers.Serializer):
    """
    Serializer for registrarion post method, validate mail and password.
    Сериалайзер для регистрации post method, валидирующий мейл и пароль.
    """
    name = serializers.CharField(max_length=50)
    surname = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],
            first_name=validated_data['name'],
            last_name=validated_data['surname'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False  # Set false until email confirmation, false пока юзер не подтвердил регистрацию
        )
        return user


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for catalog get, get name and category.
    Сериалайзер для catalog get, берет имя и категорию.
    """
    category = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ('name', 'category',)


class ProductParameterSerializer(serializers.ModelSerializer):
    """
    Serializer for catalog get, get parameter and value.
    Сериалайзер для catalog get, берет параметр и значение.
    """
    parameter = serializers.StringRelatedField()

    class Meta:
        model = ProductParameter
        fields = ('parameter', 'value',)


class ProductInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for catalog get, get parameters productinfo.
    Сериалайзер для catalog get, берет параметры productinfo.
    """
    product = ProductSerializer(read_only=True)
    product_parameters = ProductParameterSerializer(read_only=True, many=True)

    class Meta:
        model = ProductInfo
        fields = ('id', 'model', 'product', 'shop', 'quantity', 'price', 'price_rrc', 'product_parameters',)
        read_only_fields = ('id',)


class OrderedItemSerializer(serializers.ModelSerializer):
    """
    Serializer for each ordered_item, provides info about ordered product, include name, shop, price, quantity
    and total price for each ordered position.
    Сериализатор для заказанного товара (OrderedItem).
    Предоставляет информацию о заказанном товаре, включая наименование, магазин,
    цену, количество, и итоговую сумму для конкретного товара.
    """
    product_name = serializers.CharField(source='product_info.product.name', read_only=True)
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    price = serializers.DecimalField(source='product_info.price', max_digits=10, decimal_places=2, read_only=True)
    total = serializers.SerializerMethodField()  # Для расчета суммы

    class Meta:
        model = OrderedItem
        fields = ['id', 'product_name', 'shop_name', 'price', 'quantity', 'total']

    def get_total(self, obj):
        """
        Total price in product_info.
        Рассчитывает total сумму в product_info.
        """
        return obj.quantity * obj.product_info.price


class ContactSerializer(serializers.ModelSerializer):
    """
    Serializer for Contact, provides information about the contact, including user, city, street, house,
    structure, building, apartment, and phone.
    Сериалайзер модели контактов юзера (Contact).
    Позволяет добавлять, обновлять, удалять и просматривать адреса доставки.
    """
    class Meta:
        model = Contact
        fields = [
            'city',
            'street',
            'house',
            'structure',
            'building',
            'apartment',
        ]
        read_only_fields = ['id', 'user']

    def validate(self, attrs):
        """
        Validate:
        - User has not more than 5 addresses.
        - User has not more than 1 phone number.
        Проверяет, что:
        - Пользователь имеет не более 5 адресов.
        - Пользователь имеет не более 1 телефона.
        """
        user = self.context['request'].user

        # Validate not more 5 adresses, Проверка не более 5адресов
        existing_addresses = Contact.objects.filter(user=user).exclude(city="", street="")
        if existing_addresses.count() >= 5 and attrs.get('city') and attrs.get('street'):
            raise ValidationError("Вы можете сохранить не более 5 адресов.")

        # Validate single phone for user,Проверка одного телефона пользователя
        existing_phone = Contact.objects.filter(user=user, phone__isnull=False).exclude(phone="")
        if existing_phone.exists() and attrs.get('phone'):
            raise ValidationError("Вы можете сохранить только один номер телефона.")

        return attrs

    def create(self, validated_data):
        """
        Set the current user as the owner of the contact.
        Устанавливает текущего пользователя как владельца контакта при создании.
        """
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Updates contact data.
        Обновляет данные контакта.
        """
        return super().update(instance, validated_data)


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for Order, provides information about the order, including status, associated ordered items (orders_items),
    and total basket summary (total).
    Сериализатор Order, предоставляет информацию о заказе, включая статус, связанные заказанные элементы (orders_items),
    и общий итог корзины (total).
    """
    orders_items = OrderedItemSerializer(many=True, read_only=True)  # Serializer for ordered items, сериализатор для заказанных товаров
    total = serializers.SerializerMethodField()  #Summary total prise in basket, Поле для общего итога корзины
    status = serializers.ChoiceField(choices=['basket', 'processing', 'completed', 'canceled'], required=False)
    contact = ContactSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'orders_items', 'total', 'dt', 'contact']
        depth = 1

    def get_total(self, obj):
        """
        Summary total price in basket.
        Рассчитывает общий total итог корзины.
        """
        return sum(item.quantity * item.product_info.price for item in obj.orders_items.all())


class OrderConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming an order.
    Сериалайзер подтверждения заказа.
    """
    basket_id = serializers.IntegerField()
    contact_id = serializers.IntegerField()


class OrderListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing user orders.
    Сериалайзер вывода списка заказов пользователя.
    """
    total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'dt', 'total', 'status']

    def get_total(self, obj):
        return obj.total_price


