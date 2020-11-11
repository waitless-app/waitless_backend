from rest_framework import serializers

from core.models import Menu, Product, Premises

from premises.serializers import PremisesSerializer




class ProductSerializer(serializers.ModelSerializer):
    """ serializer to product object"""

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('id',)

class ProductListingSerializer(serializers.ModelSerializer):
    """ serializer to list product for orders"""

    class Meta:
        model = Product
        fields = ['name','price','description']

class MenuSerializer(serializers.ModelSerializer):
    """ serializer to menu object"""

    class Meta:
        model = Menu
        fields = '__all__'
        read_only_fields = ('id',)

class MenuProductsSerializer(serializers.ModelSerializer):
    products = ProductListingSerializer(many=True)
    premises = PremisesSerializer()
    class Meta:
        model = Menu
        fields = '__all__'
