import pytest
from model_bakery import baker
from users.tests import api_client


@pytest.fixture
def shop_factory():
    """
    Фабрика для магазинов.
    """
    def func(**kwargs):
        return baker.make('shop', **kwargs)

    return func


@pytest.fixture
def product_info_factory(shop_factory, product_factory):
    """
    Фабрика для информация по товару.
    """
    def func(**kwargs):
        kwargs.setdefault('price', 100)
        kwargs.setdefault('price_rrc', 100)
        shop = kwargs.pop('shop', shop_factory())
        product = kwargs.pop('product', product_factory())
        return baker.make('ProductInfo', shop=shop, product=product, **kwargs)

    return func


@pytest.fixture
def product_factory():
    """
    Фабрика для товаров.
    """
    def func(**kwargs):
        return baker.make('product', **kwargs)

    return func


@pytest.fixture
def category_factory():
    """
    Фабрика для категорий.
    """
    def func(**kwargs):
        return baker.make('category', **kwargs)

    return func


@pytest.fixture
def parameter_factory():
    def func(**kwargs):
        return baker.make('Parameter', **kwargs)

    return func


@pytest.fixture
def product_parameter_factory(product_info_factory, parameter_factory):
    """
    Фабрика для параметров продукта.
    """
    def func(**kwargs):
        quantity = kwargs.pop('_quantity', None)
        parameters = kwargs.pop('parameter', parameter_factory(_quantity=quantity))
        kwargs.setdefault('product_info', product_info_factory())
        if isinstance(parameters, list):
            return [baker.make('ProductParameter', parameter=parameter, **kwargs) for parameter in parameters]
        return baker.make('ProductParameter', parameter=parameters, **kwargs)
    return func
