from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from orders import serializers
from core.models import Order
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status

from orders.serializers import ReadOnlyOrderSerializer


class OrderView(viewsets.ReadOnlyModelViewSet):
    """Handles creating, reading updating Orders"""
    lookup_field = 'id'
    lookup_url_kwarg = 'order_id'
    permission_classes = (IsAuthenticated,)
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

    def retrieve(self, request, pk=None):
        queryset = Order.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(user)
        return Response(serializer.data)


@api_view(['POST'])
def confirm_pickup_code(request):
    try:
        pickup_code = request.data['pickup_code']
        instance = Order.objects.get(pickup_code=pickup_code)
        serializer = ReadOnlyOrderSerializer(instance)

        return Response(serializer.data)
    except (Order.DoesNotExist, KeyError):
        return Response(status=status.HTTP_404_NOT_FOUND,
                        data={'message': 'Code is invalid'})
