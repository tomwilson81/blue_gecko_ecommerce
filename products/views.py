import stripe

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Product, OrderItem, Order, BillingAddress, Payment
from django.views.generic import ListView, DetailView, View
from .forms import CheckoutForm
from django.utils import timezone

#stripe.api_key = settings.STRIPE_SECRET_KEY


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


class CheckoutView(View):
    def get(self, *args, **kwargs):
        # form
        form = CheckoutForm()
        context = {
            'form': form
        }
        return render(self.request, 'products/checkout.html', context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                # same_shipping_address = form.cleaned_data.get('same_shipping_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()

                if payment_option == 'S':
                    return redirect("products:payment", payment_option='stripe')
                elif payment_option == 'P':
                    return redirect("products:payment", payment_option='paypal')
                else:
                    messages.warning(self.request, "Invalid payment option selected")
                    return redirect('products:checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order.")
            return redirect('products:order-summary')


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'order': order
        }
        return render(self.request, 'products/payment.html', context)

    def post(self, *args, **kwargs):
        stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"
        # `source` is obtained with Stripe.js; see https://stripe.com/docs/payments/accept-a-payment-charges#web-create-token
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total() * 100)

        try:
            charge = stripe.Charge.create(
                amount=amount,  # cents
                currency="usd",
                source=token,
            )

            # create the payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            # assign the payment to the order

            order.ordered = True
            order.payment = payment
            order.save()

            messages.success(self.request, "Your order was successful.")
            return redirect("/")

        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, f"{err.get('message')}")

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, "Rate limit error")
            return redirect("/")

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.error(self.request, "Invalid parameters")
            return redirect("/")

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request, "Not authenticated")
            return redirect("/")

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request, "Network error")
            return redirect("/")

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(self.request, "Oops, something went wrong. You were not charged. Please try again.")
            return redirect("/")

        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            # send an email to ourselves
            messages.error(self.request, "A serious error occurred. We have been notified.")
            return redirect("/")


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


