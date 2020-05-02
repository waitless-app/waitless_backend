from core.models import Order
from rest_framework import serializers
from user.serializers import UserSerializer


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

        read_only_fields = ('id', 'created', 'updated')


class ReadOnlyOrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    employee = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
