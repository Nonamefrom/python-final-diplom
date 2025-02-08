from celery import shared_task
from django.core.mail import send_mail


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
