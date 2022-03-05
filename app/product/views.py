from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Menu, Product

from product import serializers


class MenuViewset(viewsets.ModelViewSet):
    """Manage menu in the database"""
    permission_classes = (IsAuthenticated,)
    queryset = Menu.objects.all()
    serializer_class = serializers.MenuSerializer

    @action(detail=True, methods=['post'])
    def make_default(self, request, **kwargs):
        instance = self.get_object()

        Menu.objects.filter(premises=instance.premises).update(is_default=False)
        instance.is_default = True
        instance.save()

        return Response(status=status.HTTP_200_OK)


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
                return self.queryset.filter(
                    premises__owner=self.request.user, premises=premises)
            # TODO create wrapper for header
            if(self.request.META['HTTP_X_SOURCE_WEB']):
                return self.queryset.filter(premises__owner=self.request.user)
        except KeyError:
            return self.queryset.none()
