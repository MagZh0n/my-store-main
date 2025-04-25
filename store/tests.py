from django.test import TestCase
from django.contrib.auth.models import User
from .models import Product, Order, Cart, CartItem, OrderItem
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


class ProductModelTest(TestCase):
    def test_create_product(self):
        product = Product.objects.create(
            name='Test Product',
            description='Test Description',
            price=10.99,
            stock=100  
        )
        self.assertEqual(product.name, 'Test Product')
        self.assertEqual(product.price, 10.99)
        self.assertEqual(product.stock, 100)


class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_create_order(self):
        order = Order.objects.create(user=self.user, total_price=50.00)
        self.assertEqual(order.user.username, 'testuser')
        self.assertEqual(order.total_price, 50.00)


class CartModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser')
        self.product = Product.objects.create(name='Product A', description='desc', price=20.0, stock=5)

    def test_create_cart_and_cart_item(self):
        cart = Cart.objects.create(user=self.user)
        item = CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        self.assertEqual(cart.user.username, 'testuser')
        self.assertEqual(item.quantity, 2)


class OrderItemModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser')
        self.product = Product.objects.create(name='Product A', description='desc', price=30.0, stock=10)
        self.order = Order.objects.create(user=self.user, total_price=60.0)

    def test_create_order_item(self):
        item = OrderItem.objects.create(order=self.order, product=self.product, quantity=2, price=30.0)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.product.name, 'Product A')
        self.assertEqual(item.price, 30.0)


class APITestCaseBase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.product = Product.objects.create(name='Кроссовки', price=15000, stock=10)


class ProductAPITests(APITestCaseBase):
    def test_product_list(self):
        url = reverse('api-product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('name' in response.data[0])

    def test_product_detail(self):
        url = reverse('api-product-detail', args=[self.product.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.product.name)


class CartAPITests(APITestCaseBase):
    def test_add_to_cart(self):
        url = reverse('api-add-to-cart', args=[self.product.id])
        response = self.client.post(url, {'quantity': 3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Product added to cart')

    def test_add_to_cart_with_invalid_quantity(self):
        url = reverse('api-add-to-cart', args=[self.product.id])
        response = self.client.post(url, {'quantity': 999})  
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cart_requires_authentication(self):
        self.client.logout()
        url = reverse('api-cart')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

