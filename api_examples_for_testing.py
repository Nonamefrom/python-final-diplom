import requests
from pprint import pprint

url = "http://127.0.0.1:8000/api/v1/"  # Замените URL на ваш


# Для тестирования POST Login юзера.
data = {
    "email": "1111111@fundapk.com",
    "password": "123456!kop"
}

response = requests.post(f'{url}user/login', json=data)
print(response.status_code)
print(response.json())


"""
# Для тестирования POST регистрации и подтверждения по ссылке
data = {
    "name":"TestName",
    "surname":"TestSurName",
    "email": "1111111@fundapk.com",
    "password": "123456!kop"
}

response = requests.post(f'{url}user/register', json=data)
print(response.status_code)
print(response.json())
"""

"""
# Для тестирования GET запросов к API каталога, с фильтрами
response = requests.get(f'{url}products/?search=MI Toothbrush')
print(response.status_code)
pprint(response.json())

GET /products/?shop_id=1
GET /products/?category_id=2
GET /products/?search=Smartphone
GET /products/?min_price=500&max_price=1000
"""

"""
# Для тестирования GET запросов к API корзины

basket_response = requests.get(f'{url}basket/', headers=headers)
# Вывод результата
print(f"Status code: {basket_response.status_code}")
pprint("Response:", basket_response.json())
"""
"""
# Для тестирования POST запросов к API корзины
POST /basket/
Authorization: Bearer <token>
Content-Type: application/json

{
    "product_info_id": 10,
    "quantity": 3
}

# Для тестирования PUT запросов к API корзины
PUT /basket/id/
Authorization: Bearer <token>
Content-Type: application/json

{
    "quantity": 5
}
# Для тестирования DELETE запросов к API корзины, удаления позиции где id=5
DELETE /basket/5/
Authorization: Bearer <token>

# Добавление контакта 
POST /contacts/
Authorization: Bearer <token>
Content-Type: application/json
{
    "city": "Тверь",
        "street": "Круглая",
        "house": "21",
        "structure": "1",
        "building": "6",
        "apartment": "10",
        "phone": ""
}

# Получение списка контактов 
GET /contacts/
Authorization: Bearer <token>

Контакты реализованы ViewSet'ом, потому поддерживают редактирование и удаление

# Редактирование контакта 
PUT /contacts/id/
Authorization: Bearer <token>
Content-Type: application/json
{
    "city": "Тверь",
        "street": "Круглая",
        "house": "21",
        "structure": "1",
        "building": "6",
        "apartment": "10"
}

# Удаление контакта 
DELETE /contacts/id
Authorization: Bearer <token>
"""

"""
# Подтверждение заказа
POST /api/v1/orders/confirm_order/
Content-Type: application/json
Authorization: Token <your_token>

{
    "basket_id": 1,
    "contact_id": 5
}
"""

"""
# Получение списка заказов
GET /api/v1/orders/
Authorization: Token <your_token>
"""

"""
# Получение данных о заказе
GET /api/v1/orders/{id}/
Authorization: Token <your_token>
"""

"""
# Изменение статуса заказа
PUT /api/v1/orders/{id}/
Content-Type: application/json
Authorization: Token <your_token>

{
    "status": "new"
}
"""