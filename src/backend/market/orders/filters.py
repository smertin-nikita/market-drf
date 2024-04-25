from django_filters import rest_framework as filters, DateTimeFromToRangeFilter
from rest_framework.filters import BaseFilterBackend

from orders.models import Order, OrderStatus


class OrderFilter(filters.FilterSet):
    """
    Фильтры для заказов.
    """

    created_at = DateTimeFromToRangeFilter()
    updated_at = DateTimeFromToRangeFilter()

    class Meta:
        model = Order
        fields = ['status', 'created_at', 'updated_at', 'amount']


class OrderListFilterBackend(BaseFilterBackend):
    """
    Filter that only allows users to see their own objects and allows admins to see all objects.
    """
    def filter_queryset(self, request, queryset, view):
        if request.user.is_staff:
            return queryset.exclude(status=OrderStatus.BASKET)
        else:
            return queryset.filter(owner=request.user)
