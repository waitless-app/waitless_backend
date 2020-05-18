from rest_framework import serializers
from django.contrib.auth import get_user_model
from core.models import Premises

User = get_user_model()


class PremisesSerializer(serializers.ModelSerializer):
    """Serializer a premises"""

    class Meta:
        model = Premises
        fields = '__all__'

        read_only_fields = ('id',)


class PremisesDetailSerializer(PremisesSerializer):
    """Serialize a premises detail"""
