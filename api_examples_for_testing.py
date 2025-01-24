import requests
from pprint import pprint

url = "http://127.0.0.1:8000/api/v1/"  # Замените URL на ваш

"""
# Для тестирования POST Login юзера.
data = {
    "email": "1cijojad373@fundapk.com",
    "password": "123456!kop"
}

response = requests.post(f'{url}user/login', json=data)
print(response.status_code)
print(response.json())
"""

"""
# Для тестирования POST регистрации и подтверждения по ссылке
data = {
    "name":"TestName",
    "surname":"TestSurName",
    "email": "1cijojad373@fundapk.com",
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