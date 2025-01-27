from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Product, ProductParameter, ProductInfo, Order, OrderedItem


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


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for Order, provides information about the order, including status, associated ordered items (orders_items),
    and total basket summary (total).
    Сериализатор Order, предоставляет информацию о заказе, включая статус, связанные заказанные элементы (orders_items),
    и общий итог корзины (total).
    """
    orders_items = OrderedItemSerializer(many=True)  # Serializer for ordered items, сериализатор для заказанных товаров
    total = serializers.SerializerMethodField()  #Summary total prise in basket, Поле для общего итога корзины

    class Meta:
        model = Order
        fields = ['id', 'status', 'orders_items', 'total']

    def get_total(self, obj):
        """
        Summary total price in basket.
        Рассчитывает общий total итог корзины.
        """
        return sum(item.quantity * item.product_info.price for item in obj.orders_items.all())
