from django.contrib.gis.geos import Point
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
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
        try:
            # TODO create wrapper for header
            if(self.request.META['HTTP_X_SOURCE_WEB']):
                return self.queryset.filter(owner=self.request.user)
        except KeyError:
            return self.queryset.all()

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new premises"""
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['get'])
    def menu(self, request, **kwargs):
        instance = self.get_object()
        menu = None
        try:
            # TODO create wrapper for header
            if(self.request.META['HTTP_X_SOURCE_WEB']):
                menu = Menu.objects.filter(premises=instance)
        except KeyError:
            menu = Menu.objects.filter(premises=instance, is_default=True)
        serializer = MenuProductsSerializer(menu, many=True)
        return Response(serializer.data)


