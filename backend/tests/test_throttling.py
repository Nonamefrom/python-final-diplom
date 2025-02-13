from rest_framework.test import APITestCase
from rest_framework import status
from django.core.cache import cache
from django.contrib.auth.models import User
from rest_framework.test import APIClient

class ThrottlingTestCase(APITestCase):
    def setUp(self):
        cache.clear()
        self.url = "/api/v1/products/"
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass",
            is_active=True,   # Set active user, Устанавливаем пользователь = активен
            is_staff=True,    # Set user - staff, Делаем его персоналом (для уверенности)
        )
        self.client = APIClient()  # Use APIClient, Используем APIClient

    def test_anon_user_throttle(self):
        """
        Testing throttling for anonymous users(3 requests per minute)
        Тестируем ограничение для анонимных пользователей (3 запроса в минуту)
        """
        for _ in range(3):
            response = self.client.get(self.url)
            print(f"Запрос {_}: статус {response.status_code}")  # Debug print, отладочный принт
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 4-th request should be blocked
        # 4-й запрос должен быть заблокирован
        response = self.client.get(self.url)
        print(f"Запрос 4: статус {response.status_code}")  # Debug print, отладочный принт
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_authenticated_user_throttle(self):
        """
        Testing throttling for authenticated users(5 requests per minute)
        Тестируем ограничение для авторизованных пользователей (5 запросов в минуту)
        """
        self.client.force_authenticate(user=self.user)  # Authenticate force, Принудительно аутентифицируем

        for _ in range(5):
            response = self.client.get(self.url)
            print(f"Запрос {_}: статус {response.status_code}")  # Debug print, отладочный принт
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 6-th request should be blocked - too many requests
        # 6-й запрос должен вернуть 429 (Too Many Requests)
        response = self.client.get(self.url)
        print(f"Запрос 6: статус {response.status_code}")  # Debug print, отладочный принт
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)



