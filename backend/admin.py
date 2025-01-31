from django.contrib import admin
from .models import Shop, Product, ProductInfo, Category, Contact, Order, OrderedItem


class ProductInfoInline(admin.TabularInline):
    model = ProductInfo
    extra = 1 # Количество добавляемых пустых форм новых характеристик


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductInfoInline]


admin.site.register(Shop)
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductInfo)
admin.site.register(Contact)
admin.site.register(Order)
admin.site.register(OrderedItem)