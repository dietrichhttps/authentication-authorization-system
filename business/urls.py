from django.urls import path
from business import views

urlpatterns = [
    path('products/', views.list_products, name='list_products'),
    path('products/<int:product_id>/', views.get_product, name='get_product'),
    path('products/create/', views.create_product, name='create_product'),
    path('products/<int:product_id>/update/', views.update_product, name='update_product'),
    path('products/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('orders/', views.list_orders, name='list_orders'),
    path('orders/<int:order_id>/', views.get_order, name='get_order'),
    path('shops/', views.list_shops, name='list_shops'),
]

