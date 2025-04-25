from rest_framework import serializers
from .models import Product, Order, OrderItem, CartItem

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2)

    class Meta:
        model = OrderItem
        fields = ['product_name', 'quantity', 'product_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source='orderitem_set', many=True)

    class Meta:
        model = Order
        fields = ['user', 'created_at', 'total_price', 'status', 'shipping_address', 'items']

class OrderCreateSerializer(serializers.Serializer):
    address = serializers.CharField()
    
    def create(self, validated_data):
        user = self.context['request'].user
        address = validated_data['address']
        cart_items = CartItem.objects.filter(cart__user=user)

        if not cart_items.exists():
            raise serializers.ValidationError("Корзина пуста")

        order = Order.objects.create(user=user, address=address)

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity
            )

        cart_items.delete()

        return order
