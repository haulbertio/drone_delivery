# In core/views.py
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Product, Order, OrderItem, DroneMission
from .serializers import ProductSerializer, OrderSerializer, DroneMissionSerializer

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

    @action(detail=False, methods=['post'])
    def add_to_cart(self, request):
        product = Product.objects.get(pk=request.data['product_id'])
        order, created = Order.objects.get_or_create(customer=request.user, order_status='pending')
        order_item, item_created = OrderItem.objects.get_or_create(order=order, product=product)
        order_item.quantity += int(request.data['quantity'])
        order_item.save()
        return Response({'status': 'item added to cart'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        order = self.get_object()
        if order.order_status == 'completed':
            return Response({'error': 'Order already completed'}, status=status.HTTP_400_BAD_REQUEST)
        order.order_status = 'completed'
        order.save()
        for item in order.items.all():
            item.product.stock -= item.quantity
            item.product.save()
        return Response({'status': 'order completed'}, status=status.HTTP_200_OK)

class DroneMissionViewSet(viewsets.ModelViewSet):
    queryset = DroneMission.objects.all()
    serializer_class = DroneMissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'pilot':
            return DroneMission.objects.filter(pilot=user)
        return DroneMission.objects.all()

    def perform_create(self, serializer):
        serializer.save(pilot=self.request.user)
