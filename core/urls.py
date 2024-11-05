# In core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, OrderViewSet, DroneMissionViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'drone_missions', DroneMissionViewSet, basename='drone_mission')

urlpatterns = [
    path('', include(router.urls)),
]
