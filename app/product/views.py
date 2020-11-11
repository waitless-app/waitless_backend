from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from core.models import Menu, Product

from product import serializers

class MenuViewset(viewsets.GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin):
    """Manage menu in the database"""
    permission_classes = (IsAuthenticated,)
    queryset = Menu.objects.all()
    serializer_class = serializers.MenuSerializer

    def perform_create(self, serializer):
        # TODO validation creating menu
        # in order to create menu (request.user) should
        # be the same as premises owner
        # only one menu can be default
        serializer.save()

class ProductViewset(viewsets.GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin):
    """Manage menu in the database"""
    permission_classes = (IsAuthenticated,)
    queryset = Product.objects.all()
    serializer_class = serializers.ProductSerializer

    def perform_create(self, serializer):
        # in order to create menu (request.user) should
        # be the same as premises owner
        serializer.save()

