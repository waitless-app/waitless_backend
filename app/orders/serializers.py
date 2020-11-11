from core.models import Order, Premises, OrderProduct, Product
from rest_framework import serializers
from user.serializers import UserSerializer
from product.serializers import ProductSerializer, ProductListingSerializer



class OrderProductSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all(), required=False)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = OrderProduct
        fields = '__all__'
        read_only_fields = ('id',)
        validators=[]

class OrderProductListingField(serializers.ModelSerializer):
    """ serializer for lisitng order products"""
    product = ProductListingSerializer()

    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    """ serializer for creating and updating orders"""
    order_products = OrderProductSerializer(many=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated')
    
    def create(self, validated_data):        
        order_products = validated_data.pop('order_products')
        order = Order.objects.create(**validated_data)
        if order_products:
            for product in order_products:
                OrderProduct.objects.create(order=order, **product)
        return order


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        exclude = ['premises']

class ReadOnlyOrderSerializer(serializers.ModelSerializer):
    # premises = serializers.PrimaryKeyRelatedField(queryset=Premises.objects.all())
    # above works but PremisesSerializer() does not
    # premises = PremisesSerializer()
    customer = UserSerializer(read_only=True)
    vendor = UserSerializer(read_only=True)
    order_products = OrderProductListingField(many=True)

    class Meta:
        model = Order
        fields = '__all__'



    
