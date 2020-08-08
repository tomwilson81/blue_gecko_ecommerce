from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class Category(models.Model):
    category_name = models.CharField(max_length=200)

    class Meta:
        ordering = ['category_name']

    def __str__(self):
        return self.category_name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200)
    product_description = models.TextField(max_length=2000, default='')
    #product_image = models.URLField(max_length=900, default='https://via.placeholder.com/300x400?text=No+photo')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    #slug = models.SlugField()

    def __str__(self):
        return self.product_name

    def get_absolute_url(self):
        return reverse('products:product-detail', args=[str(self.id)])


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    rating = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(5)])
    comment_text = models.TextField(max_length=2000, default='')
    date_posted = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        ordering = ['date_posted']

    def __str__(self):
        return self.user.username

