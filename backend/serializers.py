from rest_framework import serializers


"""
Serializer for login post method.
Сериалайзер для логина post method.
"""
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
