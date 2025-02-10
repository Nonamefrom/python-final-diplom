from celery import shared_task
from django.core.mail import send_mail
from easy_thumbnails.files import generate_all_aliases
from django.core.files.storage import default_storage
import os


@shared_task
def send_order_confirmation_email(order_id, email, total_price, city, street):
    """
    Async task to send an email confirmation for an order.
    Асинхронная отправка письма с подтверждением заказа.
    """
    subject = "Подтверждение заказа"
    message = f"Ваш заказ №{order_id} подтвержден! Сумма: {total_price} руб.\nАдрес доставки: {city}, {street}"


    send_mail(
        subject=subject,
        message=message,
        from_email="shop@example.com",
        recipient_list=[email],
        fail_silently=False,
    )


@shared_task
def process_product_image(image_path):
    """Создание миниатюр для загруженного изображения товара"""
    if default_storage.exists(image_path):
        generate_all_aliases(image_path, include_global=True)
        return f"Миниатюры созданы для {image_path}"
    return f"Файл {image_path} не найден"

@shared_task
def process_user_avatar(image_path):
    """Создание миниатюр для аватара пользователя"""
    if default_storage.exists(image_path):
        generate_all_aliases(image_path, include_global=True)
        return f"Миниатюры созданы для {image_path}"
    return f"Файл {image_path} не найден"
