from rest_framework import serializers

from core.models import Premises


class PremisesSerializer(serializers.ModelSerializer):
    """Serializer a premises"""

    class Meta:
        model = Premises
        fields = ('id', 'name', 'image_url', 'city')

        read_only_fields = ('id',)


class PremisesDetailSerializer(PremisesSerializer):
    """Serialize a premises detail"""
