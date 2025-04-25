from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    root_redirect, home, register,
    product_list, product_detail,
    cart, add_to_cart, remove_from_cart,
    logout_view, login_view,
    OrderCreateAPIView, OrderListAPIView, OrderViewSet,
    fake_payment, user_orders  
)
from . import views
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', root_redirect, name='root'),
    path('home/', home, name='home'),
    path('register/', register, name='register'),
    path('products/', product_list, name='product_list'),
    path('products/<int:product_id>/', product_detail, name='product_detail'),
    path('cart/', cart, name='cart'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('logout/', logout_view, name='logout'),
    path('login/', login_view, name='login'),
    path('api/orders/create/', OrderCreateAPIView.as_view(), name='order-create'),
    path('api/orders/', OrderListAPIView.as_view(), name='order-list'),
    path('api/', include(router.urls)),
    path('api/products/<int:pk>/', views.ProductDetailAPIView.as_view(), name='api-product-detail'),
    path('api/products/', views.ProductListAPIView.as_view(), name='api-product-list'),
    path('api/cart/add/<int:product_id>/', views.AddToCartAPI.as_view(), name='api-add-to-cart'),
    path('api/cart/', views.CartAPI.as_view(), name='api-cart'),
    path('pay/', fake_payment, name='fake_payment'),
    path('orders/', user_orders, name='orders'),
    path('cart/increase/<int:product_id>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:product_id>/', views.decrease_quantity, name='decrease_quantity'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)





