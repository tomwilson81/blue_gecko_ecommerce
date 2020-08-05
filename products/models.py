import datetime
from django.conf import settings
from django.db import models


class Category(models.Model):
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return self.category_name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200)
    product_description = models.CharField(max_length=2000)
    #product_image = models.ImageField()
    price = models.FloatField(default=0)

    def __str__(self):
        return self.product_name


class OrderItem(models.Model):
    item = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.product_name

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class Review(models.Model):
    user_name = models.CharField(max_length=50)
    rating = models.IntegerField(default=0)
    comment_text = models.CharField(max_length=1000)
    date_posted = models.DateTimeField('date posted')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

