from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Product, OrderItem, Order
from django.views.generic import ListView, DetailView, View
from django.utils import timezone


class HomeView(ListView):
    model = Product
    paginate_by = 10
    template_name = "products/home.html"


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, "products/order_summary.html", context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order.")
            return redirect('/')


class ProductDetailView(DetailView):
    model = Product
    template_name = "products/product.html"


def checkout(request):
    return render(request, 'products/checkout.html')

@login_required
def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    order_product, created = OrderItem.objects.get_or_create(
        product=product,
        user=request.user,
        ordered=False
        )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if ordered item is in order
        if order.product.filter(product__slug=product.slug).exists():
            order_product.quantity += 1
            order_product.save()
            messages.info(request, "The product quantity was updated in your cart.")
            return redirect("products:order-summary")
        else:
            order.product.add(order_product)
            messages.info(request, "This product was added to your cart.")
            return redirect("products:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user,
            ordered_date=ordered_date
        )
        order.product.add(order_product)
        messages.info(request, "This product was added to your cart.")
        return redirect("products:order-summary")

@login_required
def remove_from_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if ordered item is in order
        if order.product.filter(product__slug=product.slug).exists():
            order_product = OrderItem.objects.filter(
                product=product,
                user=request.user,
                ordered=False
            )[0]
            order.product.remove(order_product)
            messages.info(request, "This product was removed from your cart.")
            return redirect("products:order-summary")
        else:
            messages.info(request, "This product was not in your cart.")
            return redirect("products:product-detail", slug=slug)
    else:
        messages.info(request, "You do not have an active cart.")
        return redirect("products:product-detail", slug=slug)

@login_required
def remove_single_item_from_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if ordered item is in order
        if order.product.filter(product__slug=product.slug).exists():
            order_product = OrderItem.objects.filter(
                product=product,
                user=request.user,
                ordered=False
            )[0]
            if order_product.quantity > 1:
                order_product.quantity -= 1
                order_product.save()
            else:
                order.product.remove(order_product)
            messages.info(request, "This product quantity was updated.")
            return redirect("products:order-summary")
        else:
            messages.info(request, "This product was not in your cart.")
            return redirect("products:product-detail", slug=slug)
    else:
        messages.info(request, "You do not have an active cart.")
        return redirect("products:product-detail", slug=slug)




# def home_page(request):
#     categories = Category.objects.all()
#     products = Product.objects.all()
#     context = {
#         'products': products,
#         'categories': categories,
#     }
#     return render(request, 'products/home.html', context)


# def category_product_list(request, category_id):
#     categories = Category.objects.get(pk=category_id)
#     products = Product.objects.filter(category__id=category_id)
#     context = {
#         'products': products,
#         'categories': categories,
#     }
#     return render(request, 'products/home.html', context)


# def product_detail(request, product_id):
#     categories = Category.objects.all()
#     products = Product.objects.get(pk=product_id)
#     #review_qs = product.review_set.all()
#     context = {
#         'products': products,
#         'categories': categories,
#         #'reviews': review_qs
#     }
#     return render(request, 'products/product.html', context)


