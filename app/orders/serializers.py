from core.models import Order, Premises
from rest_framework import serializers
from user.serializers import UserSerializer

class PremisesSerializer(serializers.ModelSerializer):
    """Serializer a premises"""

    class Meta:
        model = Premises
        fields = '__all__'

        read_only_fields = ('id',)

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated')

class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class ReadOnlyOrderSerializer(serializers.ModelSerializer):
    # premises = serializers.PrimaryKeyRelatedField(queryset=Premises.objects.all())

    premises = PremisesSerializer()
    customer = UserSerializer(read_only=True)
    vendor = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

    
