from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from core.models import Premises

from premises import serializers


class PremisesViewSet(viewsets.ModelViewSet):
    """Manage premises in database"""
    lookup_field = 'id'
    lookup_url_kwarg = 'premises_id'
    serializer_class = serializers.PremisesSerializer
    queryset = Premises.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Retreive the premises for auth user"""
        return self.queryset

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retreive':
            return serializers.PremisesDetailSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new premises"""
        serializer.save()
