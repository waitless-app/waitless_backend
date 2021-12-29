from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from core.models import Menu, Product

from product import serializers

class MenuViewset(viewsets.ModelViewSet):
    """Manage menu in the database"""
    permission_classes = (IsAuthenticated,)
    queryset = Menu.objects.all()
    serializer_class = serializers.MenuSerializer

    # def perform_create(self, serializer):
    #     # TODO validation creating menu
    #     # in order to create menu (request.user) should
    #     # be the same as premises owner
    #     # only one menu can be default
    #     serializer.save()

class ProductViewset(viewsets.ModelViewSet):
    """Manage menu in the database"""
    permission_classes = (IsAuthenticated,)
    queryset = Product.objects.all()
    serializer_class = serializers.ProductSerializer

    def get_queryset(self):
        premises = self.request.query_params.get("premises", None)
        """Retreive the premises for auth user"""
        try:
            if premises:
                return self.queryset.filter(premises__owner=self.request.user, premises=premises)
            # TODO create wrapper for header
            if(self.request.META['HTTP_X_SOURCE_WEB']):
                return self.queryset.filter(premises__owner=self.request.user)
        except KeyError:
            return self.queryset.none()

    # def perform_create(self, serializer):
    #     # in order to create menu (request.user) should
    #     # be the same as premises owner
    #     serializer.save()
    #
