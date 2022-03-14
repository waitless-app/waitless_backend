from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils import model_meta

from core.models import Order, OrderProduct, Product
from rest_framework import serializers
from user.serializers import UserSerializer
from product.serializers import ProductListingSerializer
from premises.serializers import PremisesSerializer


class OrderProductSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(), required=False)
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all())

    class Meta:
        model = OrderProduct
        fields = '__all__'
        read_only_fields = ('id',)


class OrderProductListingField(serializers.ModelSerializer):
    """ serializer for lisitng order products"""
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), required=True)

    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity']

    def to_representation(self, instance):
        self.fields['product'] = ProductListingSerializer()
        return super(OrderProductListingField,
                     self).to_representation(instance)


class OrderSerializer(serializers.ModelSerializer):
    """ serializer for creating and updating orders"""

    class Meta:
        model = Order
        fields = '__all__'
        extra_field = 'total_cost'
        read_only_fields = ('id', 'created', 'updated')

    def create(self, validated_data):
        order_products = validated_data.pop('order_products')
        order = Order.objects.create(**validated_data)
        if order_products:
            for product in order_products:
                product_id = product.get('product')
                quantity = product.get('quantity')
                OrderProduct.objects.create(
                    order=order, product=Product.objects.get(id=product_id),
                    quantity=quantity)
        return order


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        exclude = ['premises']

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)
        info = model_meta.get_field_info(instance)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)

        if instance.status == "READY":
            instance.generate_order_pickup_code()

        if instance.status == "COMPLETED":
            instance.clear_order_pickup_code()

        instance.save()

        # Note that many-to-many fields are set after updating instance.
        # Setting m2m fields triggers signals which could potentially change
        # updated instance and we do not want it to collide with .update()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance


class ReadOnlyOrderSerializer(serializers.ModelSerializer):
    premises = PremisesSerializer(read_only=True)
    customer = UserSerializer(read_only=True)
    order_products = OrderProductListingField(many=True)

    class Meta:
        model = Order
        fields = (
            'id', 'premises', 'customer', 'created', 'updated', 'ready_time',
            'collected_time', 'status',
            'order_comment', 'pickup_code', 'total_cost', 'order_products',
            'accept_time')
