from django.db import models
from django.contrib.auth.models import User


""" 
The file describes the application's DB models,
each class has an override of the base method __str__
"""
class Shop(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    url = models.URLField(max_length=200, null=True, blank=True, verbose_name='Ссылка')
    state = models.BooleanField(default=True, verbose_name='статус получения заказов')

    def __str__(self):
        return self.name


class Category(models.Model):
    shops = models.ManyToManyField(Shop, related_name='categories', verbose_name='Магазины')
    name = models.CharField(max_length=255, verbose_name='Название')

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE,
                                 verbose_name='Категория')
    name = models.CharField(max_length=255, verbose_name='Название')

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    product = models.ForeignKey(Product, related_name='product_info', on_delete=models.CASCADE,
                                verbose_name='Продукт')
    shop = models.ForeignKey(Shop,related_name='product_info', on_delete=models.CASCADE,
                             verbose_name='Магазин')
    quantity = models.IntegerField(verbose_name='Количество')
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Цена')
    price_rrc = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Рекомендуемая розничная цена')
    model = models.CharField(max_length=80, blank=True, verbose_name='Модель')
    external_id = models.IntegerField(verbose_name='Внешний ИД')

    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = "Информационный список о продуктах"
        constraints = [
            models.UniqueConstraint(fields=['product', 'shop', 'external_id'], name='unique_product_info'),
        ]


class Parameter(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo, related_name='product_parameters', on_delete=models.CASCADE,
                                     verbose_name='Информация о продукте', blank=True)
    parameter = models.ForeignKey(Parameter, related_name='product_parameters', on_delete=models.CASCADE,
                                  verbose_name='Параметр', blank=True)
    value = models.CharField(max_length=80, verbose_name='Значение')

    def __str__(self):
        return f"{self.parameter.name}: {self.value}"


class Order(models.Model):
    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE, verbose_name='Пользователь')
    dt = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, verbose_name='Статус')

    def __str__(self):
        return f"Order {self.pk} by {self.user}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='orders_items', on_delete=models.CASCADE,
                              verbose_name='Заказ')
    product = models.ForeignKey(Product, related_name='orders_items', on_delete=models.CASCADE,
                              verbose_name='Информация о продукте')
    shop = models.ForeignKey(Shop, related_name='orders_items', on_delete=models.CASCADE,
                              verbose_name=' Магазин')
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.quantity} of {self.product.name} from {self.shop.name}"


class Contact(models.Model):
    CONTACT_TYPES = [
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('address', 'Address'),
    ]
    type = models.CharField(max_length=20,choices=CONTACT_TYPES)
    user = models.ForeignKey(User, related_name='contacts', on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    value = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.type}: {self.value}"
