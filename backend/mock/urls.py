from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.get_products, name='get_products'),
    path('orders/', views.get_orders, name='get_orders'),
]
