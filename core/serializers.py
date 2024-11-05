# In core/serializers.py
from rest_framework import serializers
from .models import User, Product, Order, OrderItem, DroneMission

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'order_status', 'items', 'created_at', 'updated_at']
        read_only_fields = ['customer']

class DroneMissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DroneMission
        fields = ['id', 'order', 'pilot', 'mission_status', 'created_at', 'completed_at']
        read_only_fields = ['pilot']
