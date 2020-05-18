from core.models import Order, Premises
from rest_framework import serializers
from user.serializers import UserSerializer
from premises.serializers import PremisesSerializer


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated')

class UpdateOrderSerializer(serializers.ModelSerializer):
    premises = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all(), required=False, allow_null=True, default=None)
    class Meta:
        model = Order
        fields = '__all__'

class ReadOnlyOrderSerializer(serializers.ModelSerializer):
    # premises = PremisesSerializer(read_only=True)
    customer = UserSerializer(read_only=True)
    vendor = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
