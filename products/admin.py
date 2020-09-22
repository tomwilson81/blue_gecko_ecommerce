from django.contrib import admin

from .models import Category, Product, OrderItem, Order, Payment, Coupon, Refund, Address, UserProfile

def make_refund_approved(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_approved=True)
make_refund_approved.short_description = "Update refund to approved"

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    'being_delivered',
                    'received',
                    'refund_requested',
                    'refund_approved',
                    'billing_address',
                    'shipping_address',
                    'payment',
                    'coupon',
                    ]
    list_display_links = ['user',
        'billing_address',
        'shipping_address',
        'payment',
        'coupon']

    search_fields = ['user__username',
                     'ref_code']

    list_filter = ['user',
                    'ordered',
                    'being_delivered',
                    'received',
                    'refund_requested',
                    'refund_approved']

    actions = [make_refund_approved]

class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'country',
        'zip',
        'address_type',
        'default'
    ]
    list_filter = ['default', 'address_type', 'country']
    search_fields = ['user', 'street_address', 'apartment_address', 'zip']


admin.site.register(Category)
admin.site.register(Product)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(Address, AddressAdmin)
admin.site.register(UserProfile)



