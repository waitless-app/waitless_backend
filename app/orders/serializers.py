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
    product = ProductListingSerializer()

    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    """ serializer for creating and updating orders"""
    # order_products = serializers.RelatedField(queryset=OrderProduct.objects.all(), many=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated')

    def create(self, validated_data):
        # becuase order_products is marked as ReadOnly function is_valid does not pass in to validated_data
        order_products = validated_data.pop('order_products')
        order = Order.objects.create(**validated_data)
        if order_products:
            for product in order_products:
                OrderProduct.objects.create(order=order, product=Product.objects.get(id=product))
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

class ReadOnlyOrderSerializer(serializers.ModelSerializer):
    # premises = serializers.PrimaryKeyRelatedField(queryset=Premises.objects.all())
    # above works but PremisesSerializer() does not
    premises = PremisesSerializer(read_only=True)
    customer = UserSerializer(read_only=True)
    vendor = UserSerializer(read_only=True)
    order_products = OrderProductListingField(many=True)

    class Meta:
        model = Order
        fields = '__all__'




