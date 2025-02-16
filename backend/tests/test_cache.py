import os
from django.test import TestCase
from django.core.cache import cache
from backend.models import Product
import time


base_url = os.getenv("BASE_URL")

class CacheTestCase(TestCase):


    def test_cache_performance(self):
        """Тестируем влияние кэша на время отклика API"""
        cache.clear()  # Очистка кэша перед тестом
        self.url = f"{base_url}/api/v1/products/"
        # Первый запрос (без кэша)
        start = time.time()
        response1 = self.client.get(self.url)
        no_cache_time = time.time() - start

        # Второй запрос (с кэшем)
        start = time.time()
        response2 = self.client.get(self.url)
        cache_time = time.time() - start

        print(f"Без кэша: {no_cache_time:.5f} сек, С кэшем: {cache_time:.5f} сек")

        # Проверяем, что API отвечает корректно
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)

        # Проверяем, что кэш реально ускоряет запрос
        self.assertTrue(cache_time < no_cache_time, "Ответ с кэшем должен быть быстрее")
