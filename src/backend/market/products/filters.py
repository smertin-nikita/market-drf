from django_filters import rest_framework as filters
from rest_framework.filters import BaseFilterBackend

from products.models import ProductInfo


class ProductInfoFilter(filters.FilterSet):
    """
    Фильтры для заказов.
    """

    class Meta:
        model = ProductInfo
        fields = ['model', 'quantity', 'price', 'price_rrc']


class ProductInfoListFilterBackend(BaseFilterBackend):
    """
    Фильтрация по id продукта и по id категории продукта и по id магазина
    """
    def filter_queryset(self, request, queryset, view):
        filter_params = {}
        product_id = request.query_params.get('product')
        category_id = request.query_params.get('category')
        shop_id = request.query_params.get('shop')

        if product_id is not None:
            filter_params = {'product__id': product_id}
        if category_id is not None:
            filter_params = {'product__category__id': category_id}
        if shop_id is not None:
            filter_params = {'shop__id': shop_id}

        return queryset.filter(**filter_params)
