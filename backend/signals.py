from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile, ProductImage
from .tasks import process_product_image, process_user_avatar


@receiver(post_save, sender=UserProfile)
def generate_avatar_thumbnails(sender, instance, **kwargs):
    """
    Starting retouch avatar after downloading
    Запускаем обработку аватара после загрузки
    """
    if instance.avatar:
        process_user_avatar.delay(instance.avatar.name)

@receiver(post_save, sender=ProductImage)
def generate_product_thumbnails(sender, instance, **kwargs):
    """
    Starting retouch picture after downloading
    Запускаем обработку изображения товара после загрузки
    """
    if instance.image:
        process_product_image.delay(instance.image.name)
