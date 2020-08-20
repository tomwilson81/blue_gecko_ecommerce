from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home-page'),
    path('order-summary/', views.OrderSummaryView.as_view(), name='order-summary'),
    path('checkout/', views.checkout, name='checkout'),
    path('product/<slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('add-to-cart/<slug>/', views.add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', views.remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', views.remove_single_item_from_cart, name='remove-single-item-from-cart'),
    #path('category/<str:category_id>', views.category_product_list, name='category-prod-list'),
    #path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    #path('product/<str:product_id>', views.product_detail, name='product-detail'),

]