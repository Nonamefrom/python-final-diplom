#   Склонируйте содержимое репозитория на устройство

## Переведите контекст консоли на уровень с файлом manage.py используя команду
* cd

## Выполните создание таблиц БД командами ниже
* python manage.py makemigrations
* python manage.py migrate

## Выполните импорт файлов командой ниже
* python manage.py import_goods

## Создайте суперюзера(опционально)
* python manage.py createsuperuser

## Запустите сервер 
* python manage.py runserver