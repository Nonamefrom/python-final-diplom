#   Склонируйте содержимое репозитория 

## Переведите контекст консоли на уровень с файлом manage.py используя команду
* cd

## Выполните создание таблиц БД командами ниже
* python manage.py makemigrations
* python manage.py migrate

## Создайте суперюзера(опционально)
* python manage.py createsuperuser

## Запустите сервер 
* python manage.py runserver