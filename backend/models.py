from django.db import models

""" 
The file describes the application's DB models,
each class has an ovveride of the base method __str__
"""
class Shop(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    shops = models.ManyToManyField(Shop, related_name='categories')
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
