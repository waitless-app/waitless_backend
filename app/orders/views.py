from orders import serializers
from core.models import Order
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets


class OrderView(viewsets.ModelViewSet):
    """Handles creating, reading updating Orders"""
    permission_classes = (IsAuthenticated, )
    serializer_class = serializers.OrderSerializer
    queryset = Order.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        user = self.queryset.filter(user=self.request.user)
        return user
