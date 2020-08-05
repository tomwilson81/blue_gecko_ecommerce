from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.home_page, name='HomePage'),
    path('<int:category_id>/', views.category_view, name='CategoryView'),
    path('<int:category_id>/<int:product_id>/', views.product_detail, name='ProductDetail'),

]