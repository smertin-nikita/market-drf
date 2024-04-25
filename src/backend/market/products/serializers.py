from rest_framework import serializers

from products.models import Product, ProductInfo, Parameter, ProductParameter, Category, Shop
from users.serializers import UserSerializer


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer для товаров
    """
    category = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'category',)


class ParameterSerializer(serializers.ModelSerializer):
    """
    Serializer для параметров
    """
    class Meta:
        model = Parameter
        fields = ('id', 'name',)


class ProductParameterSerializer(serializers.ModelSerializer):
    """
    Serializer для параметров товара
    """
    parameter = ParameterSerializer(read_only=True)
    parameter_id = serializers.PrimaryKeyRelatedField(required=True, queryset=Parameter.objects.all(), write_only=True)

    class Meta:
        model = ProductParameter
        fields = ('id', 'parameter', 'value', 'parameter_id',)


class ProductInfoSerializer(serializers.ModelSerializer):
    """
    Serializer для информации о товаре
    """
    product = ProductSerializer(read_only=True)
    product_parameters = ProductParameterSerializer(many=True)
    shop_id = serializers.PrimaryKeyRelatedField(queryset=Shop.objects.all(), required=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=True, write_only=True)

    class Meta:
        model = ProductInfo
        fields = (
            'id', 'code_id', 'model', 'price', 'product', 'price_rrc',
            'quantity', 'product_parameters', 'shop_id', 'product_id'
        )

    def create(self, validated_data):
        """Create information about product."""

        product = validated_data.pop('product_id')
        shop = validated_data.pop('shop_id')
        product_parameters = validated_data.pop('product_parameters')

        product_info = ProductInfo.objects.create(**validated_data, product=product, shop=shop)

        for item in product_parameters:
            ProductParameter.objects.create(
                product_info=product_info, parameter=item.get('parameter_id'), value=item.get('value')
            )

        return product_info

    def update(self, instance, validated_data):
        """Update info about product."""

        product = validated_data.pop('product_id', None)
        shop = validated_data.pop('shop_id', None)
        product_parameters = validated_data.pop('product_parameters', None)

        if product is not None:
            instance.product = product

        if shop is not None:
            instance.shop = shop

        if product_parameters is not None:
            data_parameters = {}
            # Perform creations
            for product_parameter in product_parameters:
                value = product_parameter.get('value')
                parameter = product_parameter.get('parameter_id')

                if parameter is None:
                    raise serializers.ValidationError(
                        {"product_parameters": [{"parameter_id": ["This field is required."]}]}
                    )

                data_parameters[parameter.id] = parameter
                if not instance.product_parameters.filter(parameter=parameter).exists():
                    if value is None:
                        raise serializers.ValidationError(
                            {"product_parameters": [{"value": ["This field is required."]}]}
                        )

                    ProductParameter.objects.create(product_info=instance, parameter=parameter, value=value)

                elif value is not None:
                    obj = ProductParameter.objects.filter(product_info=instance, parameter=parameter).first()
                    obj.value = value
                    obj.save()

                # Perform deletions.
                for obj in list(instance.product_parameters.all()):
                    if obj.parameter_id not in data_parameters:
                        obj.delete()

        return super().update(instance, validated_data)

    def validate_product_parameters(self, data):
        """Checks product_parameters for empty list."""
        if not len(data):
            raise serializers.ValidationError(['The field cannot be an empty list'])

        return data


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer для категории
    """
    class Meta:
        model = Category
        fields = ('id', 'name', )


class ShopSerializer(serializers.ModelSerializer):
    """
    Serializer для магазина
    """
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Shop
        fields = ('id', 'name', 'owner',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        validated_data['owner'] = self.context["request"].user
        validated_data['owner'].is_supplier = True
        return super().create(validated_data)
