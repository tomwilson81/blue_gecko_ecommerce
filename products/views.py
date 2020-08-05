from django.shortcuts import get_object_or_404, render
from .models import Category, Product

def home_page(request):
    all_categories = Category.objects.all()
    context = {'all_categories': all_categories}
    return render(request, 'products/product_list.html', context)

def category_view(request, category_id):
    category_list = get_object_or_404(Category, pk=category_id)
    return render(request, 'products/category.html', {'category_list': category_list})

def product_detail(request, category_id, product_id):
    category_list = get_object_or_404(Category, pk=category_id)
    product_details = get_object_or_404(Product, pk=product_id)
    return render(request, 'products/product.html', {'category_list': category_list, 'product_details': product_details})
