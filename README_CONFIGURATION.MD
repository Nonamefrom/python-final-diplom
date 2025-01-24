#   Склонируйте содержимое репозитория на устройство

## Переведите контекст консоли на уровень с файлом manage.py используя команду
* cd

## Выполните создание таблиц БД командами ниже
* python manage.py makemigrations
* python manage.py migrate

## Выполните импорт файлов командой ниже, указав имя требуемого файла в файле management/commands/import_goods.py
* python manage.py import_goods

## Создайте суперюзера(опционально)
* python manage.py createsuperuser

## Запустите сервер 
* python manage.py runserver

## Проверьте настройки отправки почты в orders/settings.py, и классе RegisterAccountView расроложенного backend/view.py
*  запустите сервер локального SMTP командой(при проверке на локальном стенде)
* python -m smtpd -n -c DebuggingServer localhost:1025

## Для тестирования функционала заготовлены апи запросы в файле api_examples_for_testing.py

