from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Order, CartItem
from django.contrib.auth.forms import AuthenticationForm
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import OrderCreateSerializer, OrderSerializer, ProductSerializer
from rest_framework import generics
from rest_framework import viewsets, permissions
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from .forms import RegisterForm
from .permissions import IsOwnerOrAdmin
from django.views.decorators.csrf import csrf_exempt



def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('home')
    return redirect('register')


@login_required
def home(request):
    return render(request, 'store/home.html')


@login_required
def logout_view(request):
    auth_logout(request)
    messages.success(request, "Вы успешно вышли из системы")
    return redirect('home')


@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})


@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'store/product_detail.html', {'product': product})

@login_required
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', [])
    cart = [item for item in cart if item['product_id'] != product_id]
    request.session['cart'] = cart
    return redirect('cart')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Вы успешно вошли")
            return redirect('home')
    else:
        form = AuthenticationForm()

    return render(request, 'store/login.html', {'form': form})


def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'store/register.html', {'form': form})


class OrderCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            return Response({'error': 'Invalid quantity'}, status=status.HTTP_400_BAD_REQUEST)

        if quantity > 10:
            return Response({'error': 'You cannot add more than 10 items'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity

        cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderListAPIView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import Product, Cart, CartItem, Order, OrderItem

@login_required
def fake_payment(request):
    cart_data = request.session.get('cart', [])
    if not cart_data:
        messages.error(request, "Корзина пуста.")
        return redirect('cart')

    total_price = 0

    for item in cart_data:
        product = get_object_or_404(Product, id=item['product_id'])
        total_price += product.price * item['quantity']

    order = Order.objects.create(user=request.user, total_price=total_price)

    for item in cart_data:
        product = get_object_or_404(Product, id=item['product_id'])
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item['quantity'],
            price=product.price
        )

    request.session['cart'] = []

    messages.success(request, "Оплата прошла успешно. Заказ оформлен.")
    return redirect('orders')  







@login_required
def payment_success(request):
    if 'cart' in request.session:
        del request.session['cart']

    last_order = Order.objects.filter(user=request.user).last()

    return render(request, 'store/payment_success.html', {
        'order': last_order
    })

@login_required
def decrease_quantity(request, product_id):
    cart = request.session.get('cart', [])

    for item in cart:
        if item['product_id'] == product_id:
            if item['quantity'] > 1:
                item['quantity'] -= 1
            else:
                cart = [i for i in cart if i['product_id'] != product_id]
            break

    request.session['cart'] = cart
    return redirect('cart')

@login_required
def increase_quantity(request, product_id):
    cart = request.session.get('cart', [])

    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] += 1
            break

    request.session['cart'] = cart
    return redirect('cart')

@csrf_exempt
@login_required
def cart(request):
    cart_items = request.session.get('cart', [])
    products_in_cart = []
    total_sum = 0

    for item in cart_items:
        product = get_object_or_404(Product, id=item['product_id'])
        item_total = product.price * item['quantity']
        total_sum += item_total
        products_in_cart.append({
            'product': product,
            'quantity': item['quantity'],
            'item_total': item_total
        })

    return render(request, 'store/cart.html', {
        'cart_items': products_in_cart,
        'total_sum': total_sum,
    })



class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class AddToCartAPI(APIView):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        quantity = request.data.get('quantity', 1)
        if int(quantity) > 10:
            return Response({"error": "Количество товара не может превышать 10"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Product added to cart"})

class CartAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({"message": "Hello from CartAPI"})

@login_required
def add_to_cart(request, product_id):
    cart = request.session.get('cart', [])

    found = False
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] += 1
            found = True
            break

    if not found:
        cart.append({'product_id': product_id, 'quantity': 1})

    request.session['cart'] = cart
    return redirect('cart') 


@login_required
def user_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/orders.html', {'orders': orders})


