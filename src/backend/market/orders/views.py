from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiExample, extend_schema_view
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, OR
from rest_framework.response import Response

from orders.filters import OrderListFilterBackend, OrderFilter
from orders.models import OrderItem, Order, OrderStatus
from orders.permissions import IsAdminAndIsNotBasket, IsOwnerAndIsBasketStatus
from orders.serializers import OrderSerializer, OrderItemSerializer
from users.permissions import IsOwnerOrAdminUser


@extend_schema_view(
    list=extend_schema(
        operation_id="orders_list",
        summary="List all the orders.",
        description="Return a list of all orders.",
    ),
    retrieve=extend_schema(
        summary="Retrieve order.",
        description="Get the detail of a specific order.",
    ),
    create=extend_schema(
        summary="Create order.",
        description="Create and return order's details.",
    ),
    update=extend_schema(
        exclude=True
    ),
    partial_update=extend_schema(
        summary="Update order.",
        description="Update order details by id.",
        examples=[
         OpenApiExample(
            'Valid example',
            summary='short summary',
            description='longer description',
            value={
                "order_items": [
                    {
                        "quantity": 100,
                        "product_info_id": 1,
                    }
                ],
                "status": OrderStatus.SENT
            },
            request_only=True,
            response_only=False,
        ),
    ]
    ),
    destroy=extend_schema(
        summary="Delete parameter.",
        description="Delete parameter by id.",
    )
)
class OrderViewSet(viewsets.ModelViewSet):
    """
    Viewset для заказов.
    """
    order_item_set = OrderItem.objects.select_related('product_info')
    queryset = Order.objects.prefetch_related(Prefetch('order_items', queryset=order_item_set))
    permission_classes = [IsAuthenticated & IsOwnerOrAdminUser]
    serializer_class = OrderSerializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, OrderListFilterBackend]
    ordering_fields = ['amount', ]

    filterset_class = OrderFilter

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        return response

    def get_permissions(self):
        """Получение прав для действий."""
        if self.action == "create":
            return [IsAuthenticated()]
        elif self.action in ["partial_update", "update"]:
            return [IsAuthenticated(), OR(IsAdminAndIsNotBasket(), IsOwnerAndIsBasketStatus())]
        elif self.action == "destroy":
            return [IsAuthenticated(), OR(IsAdminUser(), IsOwnerAndIsBasketStatus())]
        else:
            return super(OrderViewSet, self).get_permissions()


@extend_schema_view(
    list=extend_schema(
        summary="List all the items in the basket.",
        description="Return a list of all items in the basket.",
    ),
    retrieve=extend_schema(
        summary="Retrieve basket item.",
        description="Get the detail of specific basket item.",
    ),
    create=extend_schema(
        summary="Create basket item.",
        description="Create and return details of basket item.",
    ),
    update=extend_schema(
        exclude=True
    ),
    partial_update=extend_schema(
        summary="Update basket item.",
        description="Update details of basket item by id.",
    ),
    destroy=extend_schema(
        summary="Delete basket item.",
        description="Delete basket item by id.",
    ),
    confirm=extend_schema(
        summary="Make new order.",
        description="Mark basket as order.",
    )
)
class BasketItemViewSet(viewsets.ModelViewSet):
    """
    Viewset для заказов в корзине.
    """
    # Permission IsOwnerUser не нужен так как пользователь получает только свои позиции из корзины
    permission_classes = [IsAuthenticated]
    serializer_class = OrderItemSerializer

    @action(methods=['PATCH'], detail=False)
    def confirm(self, request):
        order, created = Order.objects.get_or_create(status=OrderStatus.BASKET, owner=self.request.user)
        serializer = OrderSerializer(order, data={'status': OrderStatus.NEW}, context={'request': request}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        # Как только пользователь запросит экземпляр в корзине создаем заказ со статусом корзины.
        # Далее используем заказ как корзину пока пользователь не подтвердит заказ
        order, _ = Order.objects.get_or_create(status=OrderStatus.BASKET, owner=self.request.user)
        return order.order_items.all().select_related('product_info')
