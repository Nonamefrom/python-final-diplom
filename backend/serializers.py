from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Product, ProductParameter, ProductInfo


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
