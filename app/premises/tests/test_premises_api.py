from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Premises

from premises.serializers import PremisesSerializer, PremisesDetailSerializer

PREMISES_URL = reverse('premises:premises-list')
BASE64_IMAGE = 'data:image/png;base64,' \
               'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg== '


def sample_premises(**params):
    """Create and return sample premises"""
    owner = get_user_model().objects.create_user(
        email="owner@onboard.io",
        password="passw0rd"
    )
    defaults = {
        'name': 'Sztoss',
        'image': BASE64_IMAGE,
        'city': 'Gdynia',
        'country': 'Poland',
        'postcode': '88-888',
        'address': 'Sample Address 121',
    }
    defaults.update(params)

    serializer = PremisesSerializer(data=defaults)
    serializer.is_valid(raise_exception=True)
    return Premises.objects.create(**serializer.validated_data, owner=owner)


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
        sample_premises()
        # should be second premises created

        res = self.client.get(PREMISES_URL)

        premises = Premises.objects.all().order_by('id')
        serializer = PremisesSerializer(premises, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    # def test_premises_limited_to_user(self):
    #     """Test retreiving premises for user"""
    #     user2 = get_user_model().objects.create_user(
    #         'otheruser@sample.org',
    #         'password1'
    #     )
    #     sample_premises(user=user2)
    #     sample_premises(user=self.user)

    #     res = self.client.get(PREMISES_URL)

    #     premises = Premises.objects.filter(owner=self.user)
    #     serializer = PremisesSerializer(premises, many=True)
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(res.data), 1)
    #     self.assertEqual(res.data, serializer.data)

    def test_view_premises_detail(self):
        """Test viewing a premises detial"""
        premises = sample_premises()

        url = detail_url(premises.id)
        res = self.client.get(url)

        serializer = PremisesDetailSerializer(premises)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_premises(self):
        """Test creating premises"""
        owner = get_user_model().objects.create_user(
            email="owner@onboard.io",
            password="passw0rd"
        )
        payload = {
            'name': 'Sztoss',
            'image': BASE64_IMAGE,
            'city': 'Gdynia',
            'country': 'Poland',
            'postcode': '88-888',
            'address': 'Sample Address 121',
        }
        res = self.client.post(PREMISES_URL, payload)
        print(res.json())
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        premises = Premises.objects.get(id=res.data['id'])
        for key in payload.keys():
            # Do not check image, Base64 is not equal to FieldFile
            if key != 'image':
                self.assertEqual(payload[key], getattr(premises, key))

    def test_partial_update_premises(self):
        """Test updating premises with patch"""
        premises = sample_premises()

        payload = {
            'name': 'Viking',
        }

        url = detail_url(premises.id)
        self.client.patch(url, payload)

        premises.refresh_from_db()
        self.assertEqual(premises.name, payload['name'])

    def test_full_update_premises(self):
        """Test updating a premises with put"""
        premises = sample_premises()
        payload = {
            'name': 'New Name',
            'image': BASE64_IMAGE,
            'city': 'Warsaw',
            'address': "Peace 420"
        }

        url = detail_url(premises.id)
        self.client.put(url, payload)

        premises.refresh_from_db()

        self.assertEqual(premises.name, payload['name'])
        self.assertEqual(premises.address, payload['address'])
        self.assertEqual(premises.city, payload['city'])
