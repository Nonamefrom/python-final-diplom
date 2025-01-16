import os
import yaml
from django.core.management.base import BaseCommand
from backend.models import Category, Product, ProductInfo, Shop, Parameter, ProductParameter


def load_data_from_yaml(file_path):
    """
    This function download data from yaml file, and return that.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
    return data



"""
def import_goods(data):
    ""
    Function import goods from data to database.
    ""
    categories_map = {}

    for category in data['categories']: #Importing categories
        category_obj, created = Category.objects.get_or_create(id=category['id'],
                                                               defaults={'name': category['name']})
        categories_map[category['id']] = category_obj

    for good in data['goods']: #Importing goods
        category = categories_map.get(good['category'])
        product = Product(
            id=good['id'],
            model=good['model'],
            name=good['name'],
            price=good['price'],
            price_rrc=good['price_rrc'],
            quantity=good['quantity'],
            category=category
            )
        product.save()

        for key, value in good['parameter'].items(): #Importing parameters og goods
            product_info = ProductInfo(product=product, name=key, value=value)
            product_info.save()
            
            
"""
def import_goods(data):
    """
    Function to import goods from data to database.
    """
    shop, created = Shop.objects.get_or_create(name=data['shop'])  # Получаем или создаем магазин

    for category in data['categories']:  # Импорт категорий
        category_object, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
        category_object.shops.add(shop.id)  # Добавляем магазин в категорию
        category_object.save()

    ProductInfo.objects.filter(shop_id=shop.id).delete()  # Удаляем старые данные по товару для текущего магазина

    for item in data['goods']:  # Импорт товаров
        # Получаем или создаем продукт в базе данных
        product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])

        # Создаем информацию о товаре
        product_info = ProductInfo.objects.create(
            product_id=product.id,
            external_id=item['id'],
            model=item['model'],
            price=item['price'],
            price_rrc=item['price_rrc'],
            quantity=item['quantity'],
            shop_id=shop.id
        )

        # Импортируем параметры товара
        for name, value in item['parameters'].items():
            parameter_object, _ = Parameter.objects.get_or_create(name=name)
            ProductParameter.objects.create(
                product_info_id=product_info.id,
                parameter_id=parameter_object.id,
                value=value
            )


class Command(BaseCommand):
    help = 'Импорт товаров из YAML файла'

    def handle(self, *args, **kwargs):
        file_path = os.path.join('data', 'shop1.yaml')
        data = load_data_from_yaml(file_path)
        import_goods(data)
        self.stdout.write(self.style.SUCCESS('Успешно импортированы из %s' % file_path))
