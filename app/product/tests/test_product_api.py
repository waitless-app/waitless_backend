from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Menu, Premises, Product

from product.serializers import ProductSerializer

PRODUCT_URL = reverse('product:product-list')

BASE64_IMAGE = 'data:image/png;base64,' \
               'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg== '
def sample_product(premises, menu, **params):
    defaults = {
            'name' : 'Cerveza',
            'description' : 'Really cold American Pale Ale',
            'price' : 9.99,
            'ingredients' : 'Hop, Water, Yeast',
            'estimated_creation_time' : 5.30,
    }
    defaults.update(params)

    return Product.objects.create(premises=premises, menu=menu, **defaults)

class PublicMenuApiTest(TestCase):
    """Test the public available menu API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test login is required to retrieve menus"""
        res = self.client.get(PRODUCT_URL)

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
        self.menu = Menu.objects.create(
            premises=self.premises,
            name='Main menu'
        )

    def test_retreive_product(self):
        """Test retreiving product"""
        sample_product(menu=self.menu, premises=self.premises)
        sample_product(menu=self.menu, premises=self.premises)

        products = Product.objects.none()
        serializer = ProductSerializer(products, many=True)
        res = self.client.get(PRODUCT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_product(self):
        """ Test creating product"""
        payload = {
            'name' : 'Cerveza',
            'description' : 'Really cold American Pale Ale',
            'price' : 9.99,
            'ingredients' : 'Hop, Water, Yeast',
            'estimated_creation_time' : 5.30,
            'premises' : self.premises.id,
            'menu': self.menu.id,
            'image': BASE64_IMAGE,
        }

        res = self.client.post(PRODUCT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload['name'], res.data['name'])

    ##TD TEST UPDATE MENU
