import decimal

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from orders.models import OrderStatus


@pytest.mark.django_db
def test_retrieve_order_for_unauthorized_client(order_factory, api_client):
    # arrange
    client, _ = api_client(is_auth=False)
    order = order_factory()
    url = reverse("orders-detail", kwargs={'pk': order.id})

    # for UNAUTHORIZED client
    resp = client.get(url)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_retrieve_order_for_not_owner_client(order_factory, api_client):
    # arrange
    client, _ = api_client()
    order = order_factory()
    url = reverse("orders-detail", kwargs={'pk': order.id})

    # for NOT OWNER client
    resp = client.get(url)
    assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_retrieve_order_for_admin_client(order_factory, api_client):
    # arrange
    client, _ = api_client(is_staff=True)
    order = order_factory(status=OrderStatus.NEW)
    url = reverse("orders-detail", kwargs={'pk': order.id})

    # for Admin client
    resp = client.get(url)
    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_retrieve_order_for_owner_client(order_factory, api_client):
    # arrange
    client, user = api_client()
    order = order_factory(owner=user)
    url = reverse("orders-detail", kwargs={'pk': order.id})

    # for OWNER client
    resp = client.get(url)
    assert resp.status_code == status.HTTP_200_OK

    resp_json = resp.json()
    assert resp_json
    assert len(resp_json) == 7  # fields count
    assert resp_json['id'] == order.id
    assert resp_json['owner']['id'] == order.owner.id
    assert resp_json['status'] == order.status
    assert decimal.Decimal(resp_json['amount']) == order.amount
    for i, product in enumerate(resp_json['order_items']):
        assert product


@pytest.mark.django_db
def test_list_orders_for_unauthorized_client(api_client):
    # arrange
    client, user = api_client(is_auth=False)
    url = reverse("orders-list")

    # for UNAUTHORIZED client
    resp = client.get(url)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_list_orders_for_not_owner_client(api_client, order_factory):
    # arrange
    client, user = api_client()
    objs = order_factory(_quantity=10)
    url = reverse("orders-list")

    # for NOT OWNER client
    resp = client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert resp_json['count'] == 0


@pytest.mark.django_db
def test_list_orders_for_owner_client(api_client, order_factory):
    # arrange
    client, user = api_client()
    objs = order_factory(_quantity=10, owner=user)
    url = reverse("orders-list")

    # for OWNER client
    resp = client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert resp_json['count'] == len(objs)


@pytest.mark.django_db
def test_list_orders_for_admin_client(api_client, order_factory, order_item_factory):
    # arrange
    client, user = api_client(is_staff=True)
    orders = order_factory(_quantity=5, status='NEW')
    # +1 корзина, которая не должна быть доступна админу
    orders.append(order_factory(status='BASKET'))
    url = reverse("orders-list")

    # for supplier client
    resp = client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    # -1 корзина, которая не должна быть доступна поставщику
    assert resp_json['count'] == len(orders) - 1


@pytest.mark.django_db
def test_filter_status_orders(api_client, order_factory):
    # arrange
    client, user = api_client(is_staff=True)
    order_factory(_quantity=5)
    test_status = 'CONFIRMED'
    order_factory(status=test_status)

    url = reverse("orders-list")

    # for Admin client
    resp = client.get(url, {'status': test_status})
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()['results']
    assert resp_json[0]['status'] == test_status


@pytest.mark.django_db
def test_order_filter_amount_orders(api_client, order_factory):
    # arrange
    client, user = api_client(is_staff=True)
    objs = order_factory(_quantity=5, status=OrderStatus.NEW)
    max_amount = max(obj.amount for obj in objs)
    min_amount = min(obj.amount for obj in objs)

    url = reverse("orders-list")

    # for Admin client
    resp = client.get(url, {'ordering': 'amount'})
    assert resp.status_code == status.HTTP_200_OK
    result = resp.json()['results']
    assert decimal.Decimal(result[0]['amount']) == decimal.Decimal(min_amount)
    assert decimal.Decimal(result[-1]['amount']) == decimal.Decimal(max_amount)


@pytest.mark.django_db
def test_filter_create_at_orders(api_client, order_factory):

    # arrange
    client, user = api_client(is_staff=True)
    orders = order_factory(_quantity=5, status=OrderStatus.NEW)
    url = reverse("orders-list")

    # act
    resp = client.get(url, {'created_at_after': orders[0].created_at, 'created_at_before': orders[0].created_at})

    # assert
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    # assert resp_json['count'] == 1


@pytest.mark.django_db
def test_filter_updated_at_orders(api_client, order_factory):

    # arrange
    client, user = api_client(is_staff=True)
    orders = order_factory(_quantity=10, status=OrderStatus.NEW)
    url = reverse("orders-list")

    # act
    resp = client.get(url, {'updated_at_after': orders[0].updated_at, 'updated_at_before': orders[0].updated_at})

    # assert
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    assert resp_json['count'] == 1


@pytest.mark.django_db
def test_create_order_for_unauthorized_client(api_client):
    # arrange
    client, user = api_client(is_auth=False)
    url = reverse("orders-list")

    # for UNAUTHORIZED client
    resp = client.post(url, format='json')
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_create_order_for_authorized_client(api_client, product_info_factory, product_factory):
    # arrange
    client, user = api_client()

    products = product_info_factory(_quantity=3, price=100, product=product_factory())
    # _quantity=3 * price=100
    test_amount = 3 * 100
    # quantity for order items is 1
    payload = {
        'order_items': ({'product_info_id': item.id}for item in products)
    }

    url = reverse("orders-list")

    # for AUTH client
    resp = client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_201_CREATED

    resp_json = resp.json()
    assert resp_json
    assert len(resp_json) == 7  # fields count
    assert resp_json['owner']['id'] == user.id
    assert decimal.Decimal(resp_json['amount']) == decimal.Decimal(test_amount)
    for i, item in enumerate(resp_json['order_items']):
        assert item['product_info']['id'] == products[i].id


@pytest.mark.django_db
def test_validate_product_is_over_on_create_order(api_client, product_info_factory, product_factory):
    # arrange
    client, user = api_client()

    product = product_info_factory(quantity=0, product=product_factory())
    payload = {
        'order_items': [{'product_info_id': product.id}]
    }

    url = reverse("orders-list")

    # for AUTH client
    resp = client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_validate_without_order_items_on_create_order(api_client):
    # without order_items
    client, user = api_client()
    payload = {}
    url = reverse("orders-list")
    # for AUTH client
    resp = client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_validate_empty_order_items_on_create_order(api_client):
    # empty order_positions
    client, user = api_client()
    payload = {"order_items": []}
    url = reverse("orders-list")
    resp = client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_validate_miss_product_info_id_in_order_items_on_create_order(api_client):
    # empty order_items
    client, user = api_client()
    payload = {"order_items": [{}]}
    url = reverse("orders-list")
    resp = client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_validate_not_exists_product_in_order_items_on_create_order(api_client, product_factory):
    client, user = api_client()
    product = product_factory()
    # NOT EXIST PRODUCT
    payload = {
        "order_items": [{'product_info_id': product.id + 1}]
    }
    url = reverse("orders-list")
    # for AUTH client
    resp = client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize(
    ["order_status", "expected_status"],
    (
        ("NEW", 'BASKET'),
        ("fsd", 'BASKET'),
        ("CONFIRMED", 'BASKET'),
    )
)
@pytest.mark.django_db
def test_validate_status_on_create_order(order_status, expected_status, api_client, product_info_factory,
                                         product_factory):
    client, user = api_client()
    products = product_info_factory(_quantity=3, price=100, product=product_factory())
    payload = {
        "order_items": ({'product_info_id': item.id}for item in products),
        "status": order_status
    }
    url = reverse("orders-list")
    # for AUTH client
    resp = client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_201_CREATED
    resp_json = resp.json()
    assert resp_json['status'] == expected_status


@pytest.mark.django_db
def test_update_order_for_unauthorized_client(api_client, order_factory):
    # arrange
    client, user = api_client(is_auth=False)
    order = order_factory()
    payload = {
        'status': 'CONFIRMED'
    }
    url = reverse("orders-detail", kwargs={'pk': order.id})

    # for UNAUTHORIZED client
    resp = client.patch(url, payload, format='json')
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_update_order_items_in_order_for_owner_client(api_client, product_info_factory, order_factory, product_factory):
    # arrange
    client, user = api_client()
    order = order_factory(owner=user)
    products = product_info_factory(_quantity=3, price=100, product=product_factory())
    # _quantity=3 * price=100
    test_amount = 3 * 100
    # quantity for order items is 1
    payload = {
        "order_items": ({'product_info_id': item.id} for item in products),
    }

    # for OWNER client
    # update
    url = reverse("orders-detail", kwargs={'pk': order.id})
    resp = client.patch(url, payload, format='json')
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert resp_json
    assert len(resp_json) == 7  # fields count
    assert resp_json['owner']['id'] == user.id
    assert decimal.Decimal(resp_json['amount']) == decimal.Decimal(test_amount)
    for i, item in enumerate(resp_json['order_items']):
        assert item['product_info']['id'] == products[i].id
    assert resp_json['status'] == OrderStatus.BASKET


@pytest.mark.django_db
def test_update_status_in_order_for_owner_client(api_client, product_info_factory, order_factory, product_factory):
    # arrange
    client, user = api_client()
    order = order_factory(owner=user)
    payload = {
        'status': OrderStatus.NEW,
    }

    # for OWNER client
    # update
    url = reverse("orders-detail", kwargs={'pk': order.id})
    resp = client.patch(url, payload, format='json')
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_status_in_order_for_admin_client(api_client, order_factory):
    # arrange
    client, user = api_client(is_staff=True)
    order = order_factory(status='NEW')
    payload = {
        'status': OrderStatus.CANCELLED,
    }

    # for supplier client
    # update
    url = reverse("orders-detail", kwargs={'pk': order.id})
    resp = client.patch(url, payload, format='json')
    print(resp.rendered_content)
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert resp_json['status'] == payload['status']


@pytest.mark.django_db
def test_update_status_on_basket_in_order_for_admin_client(api_client, order_factory):
    # arrange
    client, user = api_client(is_staff=True)
    order = order_factory(status='NEW')
    payload = {
        'status': OrderStatus.BASKET,
    }

    # for supplier client
    # update
    url = reverse("orders-detail", kwargs={'pk': order.id})
    resp = client.patch(url, payload, format='json')
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_order_items_in_order_for_admin_client(api_client, product_info_factory, order_factory):
    # arrange
    client, user = api_client(is_staff=True)
    product_info = product_info_factory()
    order = order_factory(status='NEW')
    payload = {
        "order_items": {'product_info_id': product_info.id},
    }

    # for supplier client
    # update
    url = reverse("orders-detail", kwargs={'pk': order.id})
    resp = client.patch(url, payload, format='json')
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_order_for_unauthorized_client(api_client, order_factory):
    # arrange
    client, user = api_client(is_auth=False)
    order = order_factory()

    # UNAUTHORIZED
    url = reverse("orders-detail", kwargs={'pk': order.id})
    resp = client.delete(url)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_delete_order_for_owner_client(api_client, order_factory):
    # arrange
    client, user = api_client()
    order = order_factory(owner=user)

    # for owner
    url = reverse("orders-detail", kwargs={'pk': order.id})
    resp = client.delete(url)
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_order_for_admin_client(api_client, order_factory):
    # arrange
    client, user = api_client(is_staff=True)
    order = order_factory(status=OrderStatus.NEW)

    # for admin
    url = reverse("orders-detail", kwargs={'pk': order.id})
    resp = client.delete(url)
    assert resp.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_delete_order_for_owner_client(api_client, order_factory):
    # Можно отчистить только корзину и только владельцу
    # arrange
    client, user = api_client()
    order = order_factory(owner=user)

    # for owner
    url = reverse("orders-detail", kwargs={'pk': order.id})
    resp = client.delete(url)
    assert resp.status_code == status.HTTP_204_NO_CONTENT
