import decimal

import pytest
from rest_framework import status
from rest_framework.reverse import reverse


@pytest.mark.django_db
def test_retrieve_info_for_unauthorized_client(product_info_factory, api_client):
    # arrange
    client, _ = api_client(is_auth=False)
    info = product_info_factory()
    url = reverse("products-info-detail", kwargs={'pk': info.id})

    # for UNAUTHORIZED client
    resp = client.get(url)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_retrieve_info_for_authorized_client(product_info_factory, api_client, product_parameter_factory):
    # arrange
    client, _ = api_client()

    info = product_info_factory()
    product_parameters = product_parameter_factory(product_info=info, _quantity=3)
    url = reverse("products-info-detail", kwargs={'pk': info.id})

    # for AUTHORIZED client
    resp = client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert resp_json['id'] == info.id
    assert resp_json['code_id'] == info.code_id
    assert resp_json['model'] == info.model
    assert decimal.Decimal(resp_json['price']) == info.price
    assert decimal.Decimal(resp_json['price_rrc']) == info.price_rrc
    assert resp_json['quantity'] == info.quantity
    for i, item in enumerate(product_parameters):
        assert resp_json['product_parameters'][i]['id'] == item.id
        assert resp_json['product_parameters'][i]['value'] == item.value
        assert resp_json['product_parameters'][i]['parameter']['id'] == item.parameter.id


@pytest.mark.django_db
def test_retrieve_info_for_admin_client(product_info_factory, api_client, product_parameter_factory):
    # arrange
    client, _ = api_client(is_staff=True)

    info = product_info_factory()
    product_parameters = product_parameter_factory(product_info=info, _quantity=3)
    url = reverse("products-info-detail", kwargs={'pk': info.id})

    # for admin client
    resp = client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert resp_json['id'] == info.id
    assert resp_json['code_id'] == info.code_id
    assert resp_json['model'] == info.model
    assert decimal.Decimal(resp_json['price']) == info.price
    assert decimal.Decimal(resp_json['price_rrc']) == info.price_rrc
    assert resp_json['quantity'] == info.quantity
    for i, item in enumerate(product_parameters):
        assert resp_json['product_parameters'][i]['id'] == item.id
        assert resp_json['product_parameters'][i]['value'] == item.value
        assert resp_json['product_parameters'][i]['parameter']['id'] == item.parameter.id


@pytest.mark.django_db
def test_list_info_for_unauthorized_client(api_client):
    # arrange
    client, user = api_client(is_auth=False)
    url = reverse("products-info-list")

    # for UNAUTHORIZED client
    resp = client.get(url)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_list_info_for_authorized_client(api_client, product_info_factory):
    # arrange
    client, user = api_client()
    info = product_info_factory(_quantity=5)
    url = reverse("products-info-list")

    # for AUTHORIZED client
    resp = client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()['results']
    for i, item in enumerate(info):
        assert resp_json[i]['id'] == item.id


@pytest.mark.django_db
def test_list_info_for_admin_client(api_client, product_info_factory):
    # arrange
    client, user = api_client(is_staff=True)
    info = product_info_factory(_quantity=5)
    url = reverse("products-info-list")

    # for admin client
    resp = client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()['results']
    for i, item in enumerate(info):
        assert resp_json[i]['id'] == item.id


@pytest.mark.django_db
def test_filter_price_info_for_auth_client(api_client, product_info_factory):
    # arrange
    client, user = api_client()
    info = product_info_factory(_quantity=2)
    info[0].price = 1000
    info[0].save()
    max_value = max(obj.price for obj in info)
    min_value = min(obj.price for obj in info)
    url = reverse("products-info-list")

    # for auth client
    resp = client.get(url, {'ordering': 'price'})
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()['results']
    assert decimal.Decimal(resp_json[0]['price']) == decimal.Decimal(min_value)
    assert decimal.Decimal(resp_json[-1]['price']) == decimal.Decimal(max_value)


@pytest.mark.django_db
def test_filter_price_rrc_info_for_auth_client(api_client, product_info_factory):
    # arrange
    client, user = api_client()
    info = product_info_factory(_quantity=2)
    info[0].price_rrc = 1000
    info[0].save()
    max_value = max(obj.price_rrc for obj in info)
    min_value = min(obj.price_rrc for obj in info)
    url = reverse("products-info-list")

    # for auth client
    resp = client.get(url, {'ordering': 'price_rrc'})
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()['results']
    assert decimal.Decimal(resp_json[0]['price_rrc']) == decimal.Decimal(min_value)
    assert decimal.Decimal(resp_json[-1]['price_rrc']) == decimal.Decimal(max_value)


@pytest.mark.django_db
def test_filter_quantity_info_for_auth_client(api_client, product_info_factory):
    # arrange
    client, user = api_client()
    info = product_info_factory(_quantity=2)
    info[0].quantity = 100
    info[0].save()
    max_value = max(obj.quantity for obj in info)
    min_value = min(obj.quantity for obj in info)
    url = reverse("products-info-list")

    # for auth client
    resp = client.get(url, {'ordering': 'quantity'})
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()['results']
    assert decimal.Decimal(resp_json[0]['quantity']) == decimal.Decimal(min_value)
    assert decimal.Decimal(resp_json[-1]['quantity']) == decimal.Decimal(max_value)


@pytest.mark.django_db
def test_filter_model_orders(api_client, product_info_factory):
    # arrange
    client, user = api_client()
    info = product_info_factory(_quantity=2)
    info[0].model = 'model'
    info[0].save()
    url = reverse("products-info-list")

    # for auth client
    resp = client.get(url, {'model': info[0].model})
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()['results']
    assert resp_json[0]['model'] == info[0].model


@pytest.mark.django_db
def test_filter_search_info(api_client, product_info_factory):
    # arrange
    client, user = api_client()
    info = product_info_factory(model='model')
    product_info_factory(model='ledom')

    url = reverse("products-info-list")

    # act test model
    resp = client.get(url, {'search': info.model[:-2]})

    # assert
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()['results']
    assert len(resp_json) == 1
    assert resp_json[0]['id'] == info.id
    assert resp_json[0]['model'] == info.model


@pytest.mark.django_db
def test_create_info_for_unauthorized_client(api_client):
    # arrange
    client, user = api_client(is_auth=False)
    url = reverse("products-info-list")

    # for UNAUTHORIZED client
    resp = client.post(url, format='json')
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_create_info_for_authorized_client(api_client):
    # arrange
    client, user = api_client()
    url = reverse("products-info-list")

    # for UNAUTHORIZED client
    resp = client.post(url, format='json')
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_validate_info_for_admin_client(api_client, shop_factory):
    # arrange
    client, _ = api_client(is_staff=True)

    payload = {}
    url = reverse("products-info-list")

    # for admin client
    resp = client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_validate_empty_product_parameters_info_for_admin_client(api_client, shop_factory, product_factory):
    # arrange
    client, _ = api_client(is_staff=True)
    payload = {
        'code_id': 1111111,
        'name': 'product_name',
        'shop_id': shop_factory().id,
        'product_parameters': [],
        'product_id': product_factory().id
    }
    url = reverse("products-info-list")

    # for admin client
    resp = client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_validate_does_not_exist_product_parameter_id_info_for_admin_client(api_client, shop_factory,
                                                                            product_factory):
    # arrange
    client, _ = api_client(is_staff=True)
    payload = {
        'code_id': 1111111,
        'name': 'product_name',
        'shop_id': shop_factory().id,
        'product_parameters': [{'parameter_id': 1, 'value': '1'}],
        'product_id': product_factory().id
    }
    url = reverse("products-info-list")

    # for admin client
    resp = client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_validate_miss_product_parameter_id_and_value_info_for_admin_client(api_client, shop_factory,
                                                                            product_factory):
    # arrange
    client, _ = api_client(is_staff=True)
    payload = {
        'code_id': 1111111,
        'name': 'product_name',
        'shop_id': shop_factory().id,
        'product_parameters': [{}],
        'product_id': product_factory().id
    }
    url = reverse("products-info-list")

    # for admin client
    resp = client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_validate_does_not_exists_shop_info_for_admin_client(api_client, parameter_factory, product_factory):
    # arrange
    client, _ = api_client(is_staff=True)
    parameters = parameter_factory(_quantity=5)
    payload = {
        'code_id': 1111111,
        'shop_id': 1,
        'product_parameters': ({'parameter_id': item.id, 'value': '1'} for item in parameters),
        'product_id': product_factory().id
    }
    url = reverse("products-info-list")

    # for admin client
    resp = client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_validate_does_not_exists_product_info_for_admin_client(api_client, parameter_factory, shop_factory):
    # arrange
    client, _ = api_client(is_staff=True)
    parameters = parameter_factory(_quantity=5)
    payload = {
        'code_id': 1111111,
        'shop_id': shop_factory().id,
        'product_parameters': ({'parameter_id': item.id, 'value': '1'} for item in parameters),
        'product_id': 1
    }
    url = reverse("products-info-list")

    # for admin client
    resp = client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_info_for_admin_client(api_client, parameter_factory, shop_factory, product_factory):
    # arrange
    client, _ = api_client(is_staff=True)
    parameters = parameter_factory(_quantity=5)
    payload = {
        'code_id': 1111111,
        'product_parameters': [{'parameter_id': item.id, 'value': '1'} for item in parameters],
        'shop_id': shop_factory().id,
        'product_id': product_factory().id
    }
    url = reverse("products-info-list")

    # for admin client
    resp = client.post(url, payload, format='json')

    assert resp.status_code == status.HTTP_201_CREATED
    resp_json = resp.json()
    assert resp_json['code_id'] == payload['code_id']
    assert resp_json['product']['id'] == payload['product_id']
    assert resp_json['shop_id'] == payload['shop_id']
    for i, item in enumerate(payload['product_parameters']):
        assert resp_json['product_parameters'][i]['parameter']['id'] == item['parameter_id']
        assert resp_json['product_parameters'][i]['value'] == item['value']


@pytest.mark.django_db
def test_create_info_for_supplier_client(api_client, parameter_factory, shop_factory, product_factory):
    # arrange
    client, _ = api_client(is_supplier=True)
    parameters = parameter_factory(_quantity=5)
    payload = {
        'code_id': 1111111,
        'product_parameters': [{'parameter_id': item.id, 'value': '1'} for item in parameters],
        'shop_id': shop_factory().id,
        'product_id': product_factory().id
    }
    url = reverse("products-info-list")

    # for supplier client
    resp = client.post(url, payload, format='json')

    assert resp.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_update_validate_empty_product_parameters_info_for_admin_client(api_client, product_info_factory):
    # arrange
    client, _ = api_client(is_staff=True)
    info = product_info_factory()
    payload = {
        'product_parameters': [],
    }
    url = reverse("products-info-detail", kwargs={'pk': info.id})

    # for admin client
    resp = client.patch(url, payload, format='json')
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_update_validate_miss_parameter_id_info_for_admin_client(api_client, product_info_factory):
    # arrange
    client, _ = api_client(is_staff=True)
    info = product_info_factory()
    payload = {
        'product_parameters': [{}],
    }
    url = reverse("products-info-detail", kwargs={'pk': info.id})

    # for admin client
    resp = client.patch(url, payload, format='json')
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_update_info_for_admin_client(api_client, parameter_factory, shop_factory, product_factory,
                                      product_info_factory):
    # arrange
    client, _ = api_client(is_staff=True)
    info = product_info_factory()
    parameters = parameter_factory(_quantity=5)
    payload = {
        'code_id': 1111111,
        'product_parameters': [{'parameter_id': item.id, 'value': '1'} for item in parameters],
        'shop_id': shop_factory().id,
        'product_id': product_factory().id
    }
    url = reverse("products-info-detail", kwargs={'pk': info.id})

    # for admin client
    resp = client.patch(url, payload, format='json')
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert resp_json['code_id'] == payload['code_id']
    assert resp_json['shop_id'] == payload['shop_id']
    assert resp_json['product']['id'] == payload['product_id']
    for i, item in enumerate(payload['product_parameters']):
        assert resp_json['product_parameters'][i]['parameter']['id'] == item['parameter_id']
        assert resp_json['product_parameters'][i]['value'] == item['value']


@pytest.mark.django_db
def test_update_info_for_supplier_client(api_client, parameter_factory, shop_factory, product_factory,
                                         product_info_factory):
    # arrange
    client, _ = api_client(is_supplier=True)
    info = product_info_factory()
    parameters = parameter_factory(_quantity=5)
    payload = {
        'code_id': 1111111,
        'product_parameters': [{'parameter_id': item.id, 'value': '1'} for item in parameters],
        'shop_id': shop_factory().id,
        'product_id': product_factory().id
    }
    url = reverse("products-info-detail", kwargs={'pk': info.id})

    # for supplier client
    resp = client.patch(url, payload, format='json')
    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_delete_order_for_unauthorized_client(api_client, product_info_factory):
    # arrange
    client, user = api_client(is_auth=False)
    info = product_info_factory()

    # UNAUTHORIZED
    url = reverse("products-info-detail", kwargs={'pk': info.id})
    resp = client.delete(url)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_delete_order_for_auth_client(api_client, product_info_factory):
    # arrange
    client, user = api_client()
    info = product_info_factory()

    # for auth
    url = reverse("products-info-detail", kwargs={'pk': info.id})
    resp = client.delete(url)
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_order_for_admin_client(api_client, product_info_factory):
    # arrange
    client, user = api_client(is_staff=True)
    info = product_info_factory()

    # for admin
    url = reverse("products-info-detail", kwargs={'pk': info.id})
    resp = client.delete(url)
    assert resp.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_delete_order_for_supplier_client(api_client, product_info_factory):
    # arrange
    client, user = api_client(is_supplier=True)
    info = product_info_factory()

    # for owner
    url = reverse("products-info-detail", kwargs={'pk': info.id})
    resp = client.delete(url)
    assert resp.status_code == status.HTTP_204_NO_CONTENT
