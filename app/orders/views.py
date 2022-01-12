from orders import serializers
from core.models import Order
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from django.db.models import Q


class OrderView(viewsets.ReadOnlyModelViewSet):
    """Handles creating, reading updating Orders"""
    lookup_field = 'id'
    lookup_url_kwarg = 'order_id'
    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.ReadOnlyOrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.group == "vendor":
            # TODO for dev purpose
            # premises = self.request.query_params.get('premises', -1)
            # return Order.objects.filter(premises=premises)
            return Order.objects.filter(premises__owner=user)
        if user.group == 'customer':
            return Order.objects.filter(customer=user)
        return Order.objects.none()

