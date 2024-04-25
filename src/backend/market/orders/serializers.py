from rest_framework import serializers, status
from rest_framework.exceptions import MethodNotAllowed

from orders.models import OrderItem, Order, OrderStatus
from products.models import ProductInfo
from products.serializers import ProductInfoSerializer
from users.serializers import UserSerializer


class OrderItemSerializer(serializers.ModelSerializer):

    product_info = ProductInfoSerializer(read_only=True)
    product_info_id = serializers.PrimaryKeyRelatedField(required=True, queryset=ProductInfo.objects.all(), write_only=True)

    class Meta:
        model = OrderItem
        fields = ('product_info', 'quantity', 'product_info_id',)

    def create(self, validated_data):
        # Как только пользователь решит добавить экземпляр в корзине создаем заказ со статусом корзины.
        # Далее используем заказ как корзину пока пользователь не подтвердит заказ
        order, _ = Order.objects.get_or_create(status=OrderStatus.BASKET, owner=self.context['request'].user)
        product_info = validated_data.pop('product_info_id')
        instance = OrderItem.objects.create(order=order, product_info=product_info, **validated_data)
        return instance

    def update(self, instance, validated_data):
        product_info_id = validated_data.pop('product_info_id', False)
        if product_info_id:
            validated_data['product_info'] = product_info_id
        return super().update(instance, validated_data)

    def validate_product_info_id(self, data):
        if data.quantity == 0:
            raise serializers.ValidationError(f'Товар {data} закончился', status.HTTP_400_BAD_REQUEST)
        return data


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer для заказа.
    """
    owner = UserSerializer(
        read_only=True,
    )

    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ('id', 'amount',  'status', 'created_at', 'updated_at', 'owner', 'order_items',)
        extra_kwargs = {
            'status': {'read_only': True},
            'amount': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }

    def __init__(self, *args, **kwargs):

        # Make sure the original initialization is done first.
        super().__init__(*args, **kwargs)

        # Статус можно только обновлять
        if self.context.get('request', False):
            if self.context['request'].method in ['PUT', 'PATCH']:
                self.fields['status'].read_only = False

    def create(self, validated_data):
        """Метод для создания заказ-корзины с множеством товаров или добавления товаров к уже существующей корзине."""

        # Так как двух корзин у пользователя быть не может
        order, _ = Order.objects.get_or_create(status=OrderStatus.BASKET, owner=self.context['request'].user)
        order_items = validated_data.pop('order_items')
        for item in order_items:
            order.amount += item['product_info_id'].price * item.get('quantity', 1)
            item['product_info'] = item.pop('product_info_id')
            OrderItem.objects.create(order=order, **item)

        order.save()

        return order

    def update(self, instance, validated_data):
        """Метод для обновления заказа."""

        order_items_data = validated_data.get('order_items')
        status = validated_data.get('status')

        # Update status
        if status is not None:
            instance.status = status
            # если заказ отменен восстанавливаем кол-во товара
            if instance.status == OrderStatus.CANCELLED:
                for item in list(instance.order_items.all().select_related('product_info')):
                    item.product_info.quantity += item.quantity
                    item.product_info.save()

            # Если статус новый считаем сумму и уменьшаем кол-во товара
            if instance.status == OrderStatus.NEW:
                order_items = list(instance.order_items.all().select_related('product_info'))
                if len(order_items) == 0:
                    raise MethodNotAllowed({'message': 'Ваша корзина пустая!'})
                for item in order_items:
                    item.product_info.quantity -= item.quantity
                    item.product_info.save()
                    instance.amount += item.product_info.price * item.quantity

        # Только владелец может изменять только свой заказ-корзину
        if order_items_data is not None and instance.status == OrderStatus.BASKET:
            for item in list(instance.order_items.all()):
                item.delete()
            instance.amount = 0

            for item in order_items_data:
                item['product_info'] = item.pop('product_info_id')
                instance.amount += item['product_info'].price * item.get('quantity', 1)
                OrderItem.objects.create(order=instance, **item)

        instance.save()

        return instance

    def validate_order_items(self, data):
        """Checks order_items for empty list."""
        if not len(data):
            raise serializers.ValidationError(['The field cannot be an empty list'])

        return data
