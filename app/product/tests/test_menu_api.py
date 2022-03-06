from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Menu, Premises

from product.serializers import MenuSerializer

MENU_URL = reverse('product:menu-list')


class PublicMenuApiTest(TestCase):
    """Test the public available menu API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test login is required to retrieve menus"""
        res = self.client.get(MENU_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateMenuApiTest(TestCase):
    """Test authorized calls for menu API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'user@onboard.io',
            'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        owner = get_user_model().objects.create_user(
            email='owner@owner.com',
            password='passw0rd'
        )

        self.premises = Premises.objects.create(
            name='Fast Spot',
            image='https://via.placeholder.com/350x150',
            city='Warsaw',
            owner=owner,
            location=Point(1, 1),
            country='Poland',
            postcode='88-888',
            address='Sample Address 121',
        )

    def test_retreive_menu(self):
        """Test retreiving menu"""
        Menu.objects.create(premises=self.premises, name='Master Menu')
        Menu.objects.create(premises=self.premises, name='Second Menu')

        res = self.client.get(MENU_URL)

        menus = Menu.objects.all().order_by('name')
        serializer = MenuSerializer(menus, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_menu(self):
        """ Test creating menu"""
        payload = {
            'premises': self.premises.id,
            'name': 'Main menu',
            'description': 'Main Menu Description',
        }

        res = self.client.post(MENU_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload['name'], res.data['name'])
