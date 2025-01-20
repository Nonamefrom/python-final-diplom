from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


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
