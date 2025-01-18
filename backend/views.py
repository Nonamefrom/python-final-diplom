from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from backend.serializers import LoginSerializer


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
