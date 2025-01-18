import os
import yaml
from django.core.management.base import BaseCommand
from backend.models import Category, Product, ProductInfo, Shop, Parameter, ProductParameter


def load_data_from_yaml(file_path):
    """
    This function download data from yaml file, to variable and return that.
    Функция загружает данные из файла в переменную  data, возвращая ее в результате исполнения.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
    return data


def import_goods(data):
    """
    Function to import goods from data to database, from data variable.
    Функция импортирует данные в БД из переменной data
    """
    shop, created = Shop.objects.get_or_create(name=data['shop']) # Get or create shop, Получаем или создаем магазин

    for category in data['categories']:  # Import categories, Импорт категорий
        category_object, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
        category_object.shops.add(shop.id)  #  Add shop to category, Добавляем магазин в категорию
        category_object.save()

    ProductInfo.objects.filter(shop_id=shop.id).delete()
    # Удаляем старые данные по товару для текущего магазина
    # Delete old data in productinfo for this shop

    for item in data['goods']:  # ImportGoods, Импорт товаров
        # Get or create product in database, Получаем или создаем продукт в базе данных
        product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])

        # Create productinfo, Создаем информацию о товаре
        product_info = ProductInfo.objects.create(
            product_id=product.id,
            external_id=item['id'],
            model=item['model'],
            price=item['price'],
            price_rrc=item['price_rrc'],
            quantity=item['quantity'],
            shop_id=shop.id
        )

        # Import ProductParameter, Импортируем параметры товара
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
