from django.shortcuts import render, redirect
from .models import Category, Product
from django.views.generic import DetailView

def home_page(request):
    categories = Category.objects.all()
    products = Product.objects.filter(category__id=categories[0].id)
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'products/product_list.html', context)


def category_product_list(request, category_id):
    categories = Category.objects.get(pk=category_id)
    products = Product.objects.filter(category__id=category_id)
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'products/category.html', context)


def product_detail(request, product_id):
    #categories = Category.objects.all()
    products = Product.objects.get(pk=product_id)
    #review_qs = product.review_set.all()
    context = {
        'products': products,
        #'categories': categories,
        #'reviews': review_qs
    }
    return render(request, 'products/product.html', context)