from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status

from app.settings import MAX_PREMISES_NUM
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

    def is_vendor_app(self):
        return self.request.META['HTTP_X_SOURCE_WEB']

    def get_queryset(self):
        """Retreive the premises for auth user"""
        try:
            if self.is_vendor_app():
                return self.queryset.filter(owner=self.request.user)
        except KeyError:
            return self.queryset.all()

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        return self.serializer_class

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if self.request.user.user_premises.count() >= MAX_PREMISES_NUM:
            return Response(data={'message': f'Premises number limited to {MAX_PREMISES_NUM}'},
                            status=status.HTTP_403_FORBIDDEN)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        """Create a new premises"""
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['get'])
    def menu(self, request, **kwargs):
        instance = self.get_object()
        menu = None
        try:
            if self.is_vendor_app():
                menu = Menu.objects.filter(premises=instance).order_by('name')
        except KeyError:
            menu = Menu.objects.filter(premises=instance, is_default=True)
        serializer = MenuProductsSerializer(menu, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def statistic(self, request, **kwargs):
        instance = self.get_object()

        res = {'active_orders': instance.get_active_orders(),
               'completed_orders': instance.get_completed_orders(),
               'month_balance': instance.get_month_income(),
               'today_balance': instance.get_today_income()}

        return Response(res)
