from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Premises

from premises.serializers import PremisesSerializer, PremisesDetailSerializer


PREMISES_URL = reverse('premises:premises-list')


def sample_premises(user, **params):
    """Create and return sample premises"""
    defaults = {
        'name': 'Sztoss',
        'image_url': 'https://via.placeholder.com/350x150',
        'city': 'Gdynia',
    }
    defaults.update(params)

    return Premises.objects.create(user=user, **defaults)


def detail_url(premises_id):
    """return a premises url"""
    return reverse('premises:premises-detail', args=[premises_id])


class PublicPremisesApiTests(TestCase):
    """Test unauthenticated premises API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(PREMISES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePremisesApiTests(TestCase):
    """Test unauthenticaed premises API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@sample.org',
            'testpassword'
        )
        self.client.force_authenticate(self.user)

    def test_retrive_premises(self):
        """Test retreiving a list of premises"""
        sample_premises(user=self.user)
        sample_premises(user=self.user)

        res = self.client.get(PREMISES_URL)

        premises = Premises.objects.all().order_by('-id')
        serializer = PremisesSerializer(premises, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_premises_limited_to_user(self):
        """Test retreiving premises for user"""
        user2 = get_user_model().objects.create_user(
            'otheruser@sample.org',
            'password1'
        )
        sample_premises(user=user2)
        sample_premises(user=self.user)

        res = self.client.get(PREMISES_URL)

        premises = Premises.objects.filter(user=self.user)
        serializer = PremisesSerializer(premises, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_premises_detail(self):
        """Test viewing a premises detial"""
        premises = sample_premises(user=self.user)

        url = detail_url(premises.id)
        res = self.client.get(url)

        serializer = PremisesDetailSerializer(premises)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_premises(self):
        """Test creating premises"""
        payload = {
            'name': 'Sztoss',
            'image_url': 'https://via.placeholder.com/350x150',
            'city': 'Gdynia',
        }
        res = self.client.post(PREMISES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        premises = Premises.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(premises, key))

    def test_partial_update_premises(self):
        """Test updating premises with patch"""
        premises = sample_premises(user=self.user)

        payload = {
            'name': 'Viking',
            'image_url': 'https://via.placeholder.com/350x150',
        }

        url = detail_url(premises.id)
        self.client.patch(url, payload)

        premises.refresh_from_db()
        self.assertEqual(premises.name, payload['name'])

    def test_full_update_premises(self):
        """Test updating a premises with put"""
        premises = sample_premises(user=self.user)
        payload = {
            'name': 'Sztoss',
            'image_url': 'https://via.placeholder.com/350x150',
            'city': 'Gdańsk',
        }

        url = detail_url(premises.id)
        self.client.put(url, payload)

        premises.refresh_from_db()

        self.assertEqual(premises.name, payload['name'])
        self.assertEqual(premises.image_url, payload['image_url'])
        self.assertEqual(premises.city, payload['city'])
