from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from core.models import Premises, Menu
from rest_framework.decorators import action
from rest_framework.response import Response

from premises import serializers
from product.serializers import MenuProductsSerializer


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
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['get'])
    def menu(self, request, **kwargs):
        instance = self.get_object()
        menu = Menu.objects.filter(premises=instance)
        serializer = MenuProductsSerializer(menu, many=True)
        return Response(serializer.data)


