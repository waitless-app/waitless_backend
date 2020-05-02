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
    serializer_class = serializers.OrderSerializer
    queryset = Order.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.group == "employee":
            return Order.objects.filter(
                Q(status=Order.REQUESTED) | Q(employee=user)
            )
        if user.group == 'user':
            return Order.objects.filter(user=user)
        return Order.objects.none()
