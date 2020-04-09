from django.test import TestCase
from core.models import Order
from django.urls import reverse
from django.contrib.auth import get_user_model

from orders.serializers import OrderSerializer

from rest_framework import status
from rest_framework.test import APIClient

ORDERS_URL = reverse('orders:order_list')


def sample_order(user, **params):
    """Create and return sample order"""
    return Order.objects.create(user=user)


class PublicOrdersApiTests(TestCase):
    """Test unauthenticated orders on API"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required_listing(self):
        """Test that authentication is required to list orders"""
        res = self.client.get(ORDERS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_required_post(self):
        """Test that authentication is required to create oreder"""
        res = self.client.post(ORDERS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateOrdersApiTests(TestCase):
    """Test orders actions only for authenticated users"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@user.com',
            'password12'
        )
        self.client.force_authenticate(self.user)

    def test_retrive_orders(self):
        """Test retreving a list of orders"""
        sample_order(user=self.user)
        sample_order(user=self.user)

        res = self.client.get(ORDERS_URL)

        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_order(self):
        """Test for creating sample order"""
        payload = {
            "status" : null,
            "product" : "Kebab",
            "employee" : null,
        }
        res = self.client.post(ORDERS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
