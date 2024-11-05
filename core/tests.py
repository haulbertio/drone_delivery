# In core/tests.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Order, DroneMission
from django.contrib.auth import get_user_model

User = get_user_model()

class BaseAPITestCase(APITestCase):
    def authenticate(self, username, password):
        """Authenticate and set token for the user."""
        response = self.client.post(
            reverse('token_obtain_pair'),
            data={'username': username, 'password': password},
            format='json'
        )
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)


class OrderAPITestCase(BaseAPITestCase):
    def setUp(self):
        # Create a test customer and authenticate
        self.customer = User.objects.create_user(username='customer1', password='pass', role='customer')
        self.authenticate('customer1', 'pass')

    def test_customer_can_create_order(self):
        # Test that a customer can create an order
        url = reverse('order-list')
        data = {
            "items": [{"product_id": "123", "quantity": 2}],
        }
        response = self.client.post(url, data, format='json')
        print("Order creation response data:", response.data)  # Debug output
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_customer_order_retrieval(self):
        # Create an order as the customer
        order = Order.objects.create(customer=self.customer, order_status="Pending", items=[{"product_id": "123", "quantity": 2}])

        # Test retrieval of the order
        url = reverse('order-detail', args=[order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DroneMissionAPITestCase(BaseAPITestCase):
    def setUp(self):
        # Create test users for customer and pilot
        self.customer = User.objects.create_user(username='customer2', password='pass', role='customer')
        self.pilot = User.objects.create_user(username='pilot1', password='pass', role='pilot')

        # Authenticate as pilot
        self.authenticate('pilot1', 'pass')

        # Create an order for the mission
        self.order = Order.objects.create(customer=self.customer, order_status="Pending", items=[{"product_id": "123", "quantity": 2}])

    def test_pilot_can_create_mission(self):
        # Test that a pilot can create a drone mission for an order
        url = reverse('dronemission-list')
        data = {
            "order": self.order.id,
            "mission_status": "In Progress",
        }
        response = self.client.post(url, data, format='json')
        print("Mission creation response data:", response.data)  # Debug output
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_pilot_mission_retrieval(self):
        # Create a mission as the pilot
        mission = DroneMission.objects.create(order=self.order, pilot=self.pilot, mission_status="Pending")

        # Test retrieval of the mission
        url = reverse('dronemission-detail', args=[mission.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
