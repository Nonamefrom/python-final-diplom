from django.contrib.auth import login
from django.shortcuts import redirect
from rest_framework.authtoken.models import Token
import logging


logger = logging.getLogger(__name__)


def activate_user(strategy, details, backend, user=None, *args, **kwargs):
    """Активируем пользователя, если он был создан через social-auth."""
    if user and not user.is_active:
        user.is_active = True
        user.save()
    return {'is_active': True}


def create_token(strategy, details, backend, user=None, *args, **kwargs):
    if not user:
        logger.warning("No user found in create_token pipeline!")
        return

    token, created = Token.objects.get_or_create(user=user)
    strategy.session["auth_token"] = token.key  # Сохраняем токен в сессии

    logger.info(f"Token for {user.email}: {token.key}")


def login_user(strategy, backend, user=None, request=None, *args, **kwargs):
    """Автоматически логиним пользователя после регистрации через GitHub."""
    if user and request:
        login(request, user)
        return {'user': user}


def redirect_to_basket(strategy, details, backend, user=None, *args, **kwargs):
    session_data = strategy.session.session_key  # Получаем ключ сессии
    token = strategy.session.get("auth_token")

    logger.info(f"Session Key: {session_data}, User: {user}, Token: {token}")

    if not token:
        logger.warning(f"No token found in session for user {user}, Session Data: {strategy.session.items()}")
        return redirect("/login/")  # Если токена нет — отправляем на логин

    basket_url = f"/api/v1/basket/"
    response = redirect(basket_url)
    response["Authorization"] = f"Token {token}"  # Добавляем заголовок

    logger.info(f"Redirecting {user} to {basket_url} with Token {token}")
    return response


    return response

def save_profile(backend, user, response, *args, **kwargs):
    """Сохраняет имя, фамилию и логин GitHub в Django User"""
    logger.info(f"GitHub Response: {response}")  # Логируем ответ от GitHub

    user.first_name = response.get('first_name', '') or response.get('name', '').split()[0]
    user.last_name = response.get('last_name', '') or response.get('name', '').split()[-1]
    user.username = response.get('login', user.username)
    user.email = response.get('email', user.email)  # <-- Смотрим, что записывается

    logger.info(f"Saving user: username={user.username}, email={user.email}")
    user.save()


def create_user(strategy, details, backend, user=None, *args, **kwargs):
    """Создает пользователя с нормальным username, а не ID"""
    logger.info(f"Creating user with details: {details}")

    if user:
        return {'is_new': False}

    username = details.get('username') or details.get('login')  # <-- Используем login
    email = details.get('email')

    user = strategy.create_user(email=email, username=username)
    logger.info(f"Created user: {user.username}, email={user.email}")
    return {'is_new': True, 'user': user}

def create_token(strategy, user=None, *args, **kwargs):
    if not user:
        logger.error("No user provided to create_token!")
        return

    token, created = Token.objects.get_or_create(user=user)
    strategy.request.session["auth_token"] = token.key
    strategy.request.session.modified = True
    strategy.request.session.save()  # Принудительно сохраняем сессию
    logger.info(f"Token saved in session: {token.key} for user {user.email}")
