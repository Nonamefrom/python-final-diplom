## Код готов для работы на ОС Linux
#   Склонируйте содержимое репозитория на устройство

## Переведите контекст консоли на уровень с файлом manage.py используя команду
* cd

## Выполните создание таблиц БД командами ниже
* python manage.py makemigrations
* python manage.py migrate

## Выполните импорт файлов командой ниже, указав имя требуемого файла, в файле management/commands/import_goods.py
* python manage.py import_goods

## Создайте суперюзера(опционально)
* python manage.py createsuperuser

## Запустите сервер 
* python manage.py runserver

## Проверьте настройки отправки почты в orders/settings.py, и классе RegisterAccountView расроложенного backend/view.py
*  запустите сервер локального SMTP командой(при проверке на локальном стенде)
* python -m smtpd -n -c DebuggingServer localhost:1025

## Для тестирования функционала заготовлены примеры апи запросов в файле api_examples_for_testing.py
* При тестировании с использованием Postman Desktop, авторизацию следует передавать в качестве пары "Authorization": 'Token token_from_login' во вкладке  Headers

## SwaggerUI документация доступна по адресу http://127.0.0.1:8000/api/v1/docs/ при локальном запуске

## Для запуска сервера с поддержкой Celery необходимо выполнить следующие команды:
* В одной вкладке терминала запустить сервер
* python manage.py runserver
* Во второй вкладке терминала запустить celery 
* celery -A orders worker --loglevel=info