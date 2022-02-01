import random

from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils import model_meta

from core.models import Order, Premises, OrderProduct, Product
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from user.serializers import UserSerializer
from product.serializers import ProductSerializer, ProductListingSerializer
from premises.serializers import PremisesSerializer


class OrderProductSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all(), required=False)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = OrderProduct
        fields = '__all__'
        read_only_fields = ('id',)


class OrderProductListingField(serializers.ModelSerializer):
    """ serializer for lisitng order products"""
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=True)

    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity']

    def to_representation(self, instance):
        self.fields['product'] = ProductListingSerializer()
        return super(OrderProductListingField, self).to_representation(instance)


class OrderSerializer(serializers.ModelSerializer):
    """ serializer for creating and updating orders"""

    # order_products = serializers.RelatedField(queryset=OrderProduct.objects.all(), many=True)

    class Meta:
        model = Order
        fields = '__all__'
        extra_field = 'total_cost'
        read_only_fields = ('id', 'created', 'updated')

    def create(self, validated_data):
        # becuase order_products is marked as ReadOnly function is_valid does not pass in to validated_data
        order_products = validated_data.pop('order_products')
        order = Order.objects.create(**validated_data)
        if order_products:
            for product in order_products:
                product_id = product.get('product')
                quantity = product.get('quantity')
                OrderProduct.objects.create(order=order, product=Product.objects.get(id=product_id), quantity=quantity)
        return order

    def is_valid(self, raise_exception=False):
        assert not hasattr(self, 'restore_object'), (
                'Serializer `%s.%s` has old-style version 2 `.restore_object()` '
                'that is no longer compatible with REST framework 3. '
                'Use the new-style `.create()` and `.update()` methods instead.' %
                (self.__class__.__module__, self.__class__.__name__)
        )

        assert hasattr(self, 'initial_data'), (
            'Cannot call `.is_valid()` as no `data=` keyword argument was '
            'passed when instantiating the serializer instance.'
        )

        if not hasattr(self, '_validated_data'):
            try:
                self._validated_data = self.run_validation(self.initial_data)
            except ValidationError as exc:
                print('## VALIDATED DATA', self._validated_data)
                print('## INITIAL DATA', self.initial_data)
                print('## VALIDATION ERROR', exc)
                self._validated_data = {}
                self._errors = exc.detail
            else:
                self._errors = {}

        if self._errors and raise_exception:
            raise ValidationError(self.errors)
            # print('is_valid', self.initial_data)

        return not bool(self._errors)


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
        # TODO write tests for it
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
    # premises = serializers.PrimaryKeyRelatedField(queryset=Premises.objects.all())
    # above works but PremisesSerializer() does not
    premises = PremisesSerializer(read_only=True)
    customer = UserSerializer(read_only=True)
    order_products = OrderProductListingField(many=True)

    class Meta:
        model = Order
        fields = (
            'id', 'premises', 'customer', 'created', 'updated', 'ready_time', 'collected_time', 'status',
            'order_comment', 'pickup_code', 'total_cost', 'order_products', 'accept_time')
