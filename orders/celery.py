import os
from celery import Celery

# Указываем настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orders.settings')

# Создаём экземпляр Celery
app = Celery('orders')

# Загружаем конфигурацию Celery из Django settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматический поиск задач в `tasks.py` во всех приложениях
app.autodiscover_tasks()
