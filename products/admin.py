from django.contrib import admin

from .models import Category, Product, OrderItem, Order

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(OrderItem)
admin.site.register(Order)
