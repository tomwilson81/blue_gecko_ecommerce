import stripe

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Product, OrderItem, Order, Address, Payment, Coupon, Refund, UserProfile
from django.views.generic import ListView, DetailView, View
from .forms import CheckoutForm, CouponForm, RefundForm, PaymentForm
from django.utils import timezone

import random
import string
#stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"

def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


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
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'order': order,
                'couponform': CouponForm(),
                'DISPLAY_COUPON_FORM': True,
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )

            if shipping_address_qs.exists():
                context.update({'default_shipping_address': shipping_address_qs[0]})

            billing_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='B',
                default=True
            )

            if billing_address_qs.exists():
                context.update({'default_billing_address': billing_address_qs[0]})

            return render(self.request, 'products/checkout.html', context)
        except ObjectDoesNotExist:
            messages.info(request, "You do not have an active order.")
            return redirect("products:order-summary")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                use_default_shipping = form.cleaned_data.get('use_default_shipping')
                if use_default_shipping:
                    print("Using the default shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(self.request, "No default shipping address available")
                        return redirect("products:checkout")
                else:
                    print("User is entering a new default shipping address")
                    shipping_address1 = form.cleaned_data.get('shipping_address')
                    shipping_address2 = form.cleaned_data.get('shipping_address2')
                    shipping_country = form.cleaned_data.get('shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')
                    # same_shipping_address = form.cleaned_data.get('same_shipping_address')
                    # save_info = form.cleaned_data.get('save_info')

                    if is_valid_form([shipping_address1, shipping_country, shipping_zip]):
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            zip=shipping_zip,
                            address_type='S'
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get('set_default_shipping')
                        if set_default_shipping:
                            address_qs = Address.objects.filter(
                                user=self.request.user,
                                address_type='S',
                                default=True
                            )
                            if address_qs.exists():
                                address_qs.update(default=False)

                            shipping_address.default = True
                            shipping_address.save()
                    else:
                        messages.info(self.request, "Please fill in the required shipping address fields.")

                use_default_billing = form.cleaned_data.get('use_default_billing')
                same_billing_address = form.cleaned_data.get('same_billing_address')

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()

                elif use_default_billing:
                    print("Using the default billing address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='B',
                        default=True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(self.request, "No default billing address available")
                        return redirect("products:checkout")
                else:
                    print("User is entering a new default billing address")
                    billing_address1 = form.cleaned_data.get('billing_address')
                    billing_address2 = form.cleaned_data.get('billing_address2')
                    billing_country = form.cleaned_data.get('billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')
                    # same_billing_address = form.cleaned_data.get('same_billing_address')
                    # save_info = form.cleaned_data.get('save_info')

                    if is_valid_form([billing_address1, billing_country, billing_zip]):
                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            country=billing_country,
                            zip=billing_zip,
                            address_type='B'
                        )
                        billing_address.save()

                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get('set_default_billing')
                        if set_default_billing:
                            address_qs = Address.objects.filter(
                                user=self.request.user,
                                address_type='B',
                                default=True
                            )
                            if address_qs.exists():
                                address_qs.update(default=False)

                            billing_address.default = True
                            billing_address.save()
                    else:
                        messages.info(self.request, "Please fill in the required billing address fields.")

                payment_option = form.cleaned_data.get('payment_option')

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
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False,
            }
            userprofile = self.request.user.userprofile
            if userprofile.one_click_purchasing:
                # fetch the user's card details
                cards = stripe.Customer.list_sources(
                    userprofile.stripe_customer_id,
                    limit=3,
                    object='card',
                )
                cards_list = cards['data']
                if len(cards_list) > 0:
                    # update context with user default card
                    context.update({
                        'card': cards_list[0]
                    })
            return render(self.request, 'products/payment.html', context)
        else:
            messages.warning(self.request, "You have not added a billing address.")
            return redirect('products:checkout')

    def post(self, *args, **kwargs):
        stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"
        # `source` is obtained with Stripe.js; see https://stripe.com/docs/payments/accept-a-payment-charges#web-create-token
        order = Order.objects.get(user=self.request.user, ordered=False)
        form = PaymentForm(self.request.POST)
        userprofile = UserProfile.objects.get(user=self.request.user)
        if form.is_valid():
            token = form.cleaned_data.get('stripeToken')
            save = form.cleaned_data.get('save')
            use_default = form.cleaned_data.get('use_default')

            if save:
                if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
                    customer = stripe.Customer.retrieve(
                        userprofile.stripe_customer_id)
                    customer.sources.create(source=token)

                # allow to fetch cards
                else:
                    customer = stripe.Customer.create(
                        email=self.request.user.email,
                    )
                    customer.sources.create(source=token)
                    userprofile.stripe_customer_id = customer['id']
                    userprofile.one_click_purchasing = True
                    userprofile.save()

            amount = int(order.get_total() * 100)

            try:
                if use_default or save:
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        customer="userprofile.stripe_customer_id",
                    )

                else:
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

                order_product = order.product.all()
                order_product.update(ordered=True)
                for product in order_product:
                    product.save()

                order.ordered = True
                order.payment = payment
                order.ref_code = create_ref_code()
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

def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon

    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist.")
        return redirect("products:checkout")

class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Coupon successfully added.")
                return redirect("products:checkout")

            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order.")
                return redirect("products:order-summary")


class RefundRequestView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, 'products/request_refund.html', context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')

            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received.")
                return redirect("products:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist.")
                return redirect("products:request-refund")


