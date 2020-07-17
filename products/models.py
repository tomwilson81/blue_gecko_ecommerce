import datetime
django.db import models

class Product(models.Model):
    product_name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product_description = models.CharField(max_length=None)
    product_image = models.ImageField(upload_to=None, height_field=400px, width_field=300px, max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)


class Category(models.Model):
    category_name = models.CharField(max_length=100)


class Review(models.Model):
    user_name = models.CharField(max_length=50)
    rating = models.IntegerField(default=0)
    comment_text = models.CharField(max_length=1000)
    date_posted = models.DateTimeField('date posted')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

