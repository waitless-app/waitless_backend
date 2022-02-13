from django.contrib.gis.geos import Point
from rest_framework import serializers
from django.contrib.auth import get_user_model
from core.models import Premises

from app.serializer_custom_fields import Base64ImageField

User = get_user_model()


class PremisesSerializer(serializers.ModelSerializer):
    """Serializer a premises"""
    image = Base64ImageField(max_length=None)
    owner = serializers.ReadOnlyField(source='owner.email')
    location = serializers.HiddenField(default=Point(1, 1))

    class Meta:
        model = Premises
        fields = '__all__'

        read_only_fields = ('id',)


class PremisesDetailSerializer(PremisesSerializer):
    """Serialize a premises detail"""
