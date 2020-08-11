from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.home_page, name='home-page'),
    path('category/<str:category_id>', views.category_product_list, name='category-prod-list'),
    #path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('product/<str:product_id>', views.product_detail, name='product-detail'),
]