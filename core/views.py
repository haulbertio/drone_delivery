# In core/views.py
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from django.contrib.auth.hashers import make_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import Product, Order, OrderItem, DroneMission, User
from .serializers import ProductSerializer, OrderSerializer, DroneMissionSerializer, UserSerializer
import re

def is_strong_password(password):
    # Define strong password criteria
    return (
        len(password) >= 8 and
        re.search(r'[A-Z]', password) and
        re.search(r'[a-z]', password) and
        re.search(r'\d', password) and
        re.search(r'[@$!%*?&]', password)
    )

@api_view(['POST'])
@permission_classes([AllowAny])  # Allow unauthenticated access to this view
def signup(request):
    """Handle user registration with role selection."""
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    role = request.data.get('role')
    vessel_callsign = request.data.get('vessel_callsign', None)

    # Check required fields
    if not username or not email or not password or not role:
        return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate email
    try:
        validate_email(email)
    except ValidationError:
        return Response({'error': 'Invalid email address'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate password strength
    if not is_strong_password(password):
        return Response({
            'error': 'Password must be at least 8 characters long, '
                     'contain uppercase and lowercase letters, '
                     'a number, and a special character.'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Validate role
    if role not in ['customer', 'pilot']:
        return Response({'error': 'Role must be either customer or pilot'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if username or email is already taken
    if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
        return Response({'error': 'Username or email already exists'}, status=status.HTTP_400_BAD_REQUEST)

    # Create the user
    user = User(username=username, email=email, password=make_password(password), role=role)
    if role == 'customer':
        user.vessel_callsign = vessel_callsign
    user.save()
    
    return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Require authentication to access profile
def profile(request):
    """Retrieve authenticated user's profile information."""
    user = request.user
    profile_data = {
        "username": user.username,
        "email": user.email,
        "role": user.role,
    }
    # Include vessel_callsign if the user is a customer
    if user.role == 'customer' and hasattr(user, 'vessel_callsign'):
        profile_data["vessel_callsign"] = user.vessel_callsign
    
    return Response(profile_data, status=status.HTTP_200_OK)

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
