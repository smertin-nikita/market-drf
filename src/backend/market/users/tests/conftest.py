import pytest
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from model_bakery import baker

from users.models import UserProfile


@pytest.fixture
def api_client(shop_factory):
    """
    Фикстура для клиента API.
    """
    def func(is_auth=True, **kwargs):
        kwargs.setdefault('is_active', True)
        is_supplier = kwargs.pop('is_supplier', False)
        api_client = APIClient()
        user = baker.make(get_user_model(), **kwargs)
        UserProfile.objects.create(owner=user, is_supplier=is_supplier)
        if is_supplier:
            shop_factory(owner=user)
        if is_auth:
            token = Token.objects.create(user=user)
            api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        return api_client, user
    return func
