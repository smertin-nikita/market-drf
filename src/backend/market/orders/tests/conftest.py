import pytest
from model_bakery import baker
# do not delete
from users.tests import api_client
from products.tests import product_info_factory, product_factory, shop_factory


@pytest.fixture
def order_item_factory(product_info_factory, order_factory):
    """
    Фабрика для позиции в заказе.
    """
    def func(**kwargs):
        quantity = kwargs.pop('_quantity', None)
        infos = kwargs.pop('product_info', product_info_factory(_quantity=quantity))
        kwargs.setdefault('order', order_factory())
        if isinstance(infos, list):
            return [baker.make('OrderItem', product_info=info, **kwargs) for info in infos]
        return baker.make('OrderItem', product_info=infos, **kwargs)
    return func


@pytest.fixture
def order_factory():
    """
    Фабрика для заказов.
    """
    def func(**kwargs):
        return baker.make('order', **kwargs)
    return func

