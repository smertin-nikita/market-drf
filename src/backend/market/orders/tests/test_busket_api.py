import pytest
from rest_framework import status
from rest_framework.reverse import reverse


@pytest.mark.django_db
def test_retrieve_basket_item_for_unauthorized_client(order_item_factory, api_client):
    # arrange
    client, _ = api_client(is_auth=False)
    order_items = order_item_factory()
    url = reverse("basket-detail", kwargs={'pk': order_items.id})

    # for UNAUTHORIZED client
    resp = client.get(url)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    print(resp.rendered_content)


@pytest.mark.django_db
def test_retrieve_basket_item_for_not_owner_client(api_client, order_item_factory):
    # arrange
    client, _ = api_client()
    order_items = order_item_factory()
    url = reverse("basket-detail", kwargs={'pk': order_items.id})

    # for NOT OWNER client
    resp = client.get(url)
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    print(resp.rendered_content)


@pytest.mark.django_db
def test_retrieve_basket_item_for_admin_client(api_client, order_item_factory):
    # Админ может получать только свою корзину как покупатель
    # arrange
    client, _ = api_client(is_staff=True)
    order_items = order_item_factory()
    url = reverse("basket-detail", kwargs={'pk': order_items.id})

    # for Admin client
    resp = client.get(url)
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    print(resp.rendered_content)


@pytest.mark.django_db
def test_retrieve_basket_item_for_owner_client(api_client, order_item_factory, order_factory):
    # arrange
    client, owner = api_client()
    # Создаем неподтвержденный заказ, то есть корзину для owner. order.status = 'BASKET'
    order = order_factory(owner=owner)
    order_items = order_item_factory(order=order)
    url = reverse("basket-detail", kwargs={'pk': order_items.id})

    # for owner client
    resp = client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert resp_json['product_info']
    assert resp_json['quantity']


@pytest.mark.django_db
def test_list_basket_items_for_unauthorized_client(api_client):
    # arrange
    client, _ = api_client(is_auth=False)
    url = reverse("basket-list")

    # for UNAUTHORIZED client
    resp = client.get(url)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    print(resp.rendered_content)


@pytest.mark.django_db
def test_list_basket_items_for_not_owner_client(api_client, order_item_factory):
    # Каждый пользователь получает только свои позиции из корзины
    # arrange
    client, _ = api_client()
    # Создаем позиции в корзине не для client
    order_item_factory()
    url = reverse("basket-list")

    # for not owner client
    resp = client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()['count'] == 0


@pytest.mark.django_db
def test_list_basket_items_for_owner_client(api_client, order_item_factory, order_factory):
    # arrange
    client, owner = api_client()
    # Создаем неподтвержденный заказ, то есть корзину для owner. order.status = 'BASKET'
    order = order_factory(owner=owner)
    basket_item = order_item_factory(order=order)
    url = reverse("basket-list")

    # for owner client
    resp = client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    result = resp.json()['results']
    assert result[0]['product_info']['id'] == basket_item.product_info.id
    assert result[0]['quantity'] == basket_item.quantity


@pytest.mark.django_db
def test_create_basket_item_for_unauthorized_client(api_client):
    # arrange
    client, owner = api_client(is_auth=False)
    url = reverse("basket-list")

    # for UNAUTHORIZED client
    resp = client.post(url, format='json')
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    print(resp.rendered_content)


@pytest.mark.django_db
def test_create_basket_item_for_authorized_client(api_client, product_info_factory):
    # arrange
    client, owner = api_client()
    payload = {
        'product_info_id': product_info_factory().id,
        'quantity': 1
    }
    url = reverse("basket-list")

    # for AUTHORIZED client
    resp = client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_201_CREATED
    resp_json = resp.json()
    assert resp_json['product_info']['id'] == payload['product_info_id']
    assert resp_json['quantity'] == payload['quantity']


@pytest.mark.django_db
def test_validate_miss_product_info_id_on_create_order_item(api_client):
    # arrange
    client, owner = api_client()
    payload = {
        'quantity': 1
    }
    url = reverse("basket-list")

    # for AUTHORIZED client
    resp = client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    print(resp.rendered_content)


@pytest.mark.django_db
def test_validate_not_exists_product_info_on_create_order_item(api_client, product_info_factory):
    # arrange
    client, owner = api_client()
    payload = {
        'product_info_id': 1,
    }
    url = reverse("basket-list")

    # for AUTHORIZED client
    resp = client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    print(resp.rendered_content)


@pytest.mark.django_db
def test_update_basket_item_for_unauthorized_client(api_client, order_item_factory):
    # arrange
    client, owner = api_client(is_auth=False)
    order_item = order_item_factory()
    url = reverse("basket-detail", kwargs={'pk': order_item.id})

    # for UNAUTHORIZED client
    resp = client.patch(url, format='json')
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    print(resp.rendered_content)


@pytest.mark.django_db
def test_update_basket_item_for_admin_client(api_client, product_info_factory, order_item_factory, order_factory):
    # arrange
    # Если админ не покупатель
    client, _ = api_client(is_staff=True)
    order_item = order_item_factory()
    payload = {
        'product_info_id': product_info_factory().id,
        'quantity': 2
    }
    url = reverse("basket-detail", kwargs={'pk': order_item.id})

    # for not owner client
    resp = client.patch(url, payload, format='json')
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    print(resp.rendered_content)


@pytest.mark.django_db
def test_update_basket_item_for_not_owner_client(api_client, product_info_factory, order_item_factory, order_factory):
    # arrange
    client, _ = api_client()
    order_item = order_item_factory()
    payload = {
        'product_info_id': product_info_factory().id,
        'quantity': 2
    }
    url = reverse("basket-detail", kwargs={'pk': order_item.id})

    # for not owner client
    resp = client.patch(url, payload, format='json')
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    print(resp.rendered_content)


@pytest.mark.django_db
def test_update_product_info_basket_item_for_owner_client(api_client, product_info_factory, order_item_factory,
                                                          order_factory):
    # arrange
    client, owner = api_client()
    order = order_factory(owner=owner)
    order_item = order_item_factory(order=order)
    payload = {
        'product_info_id': product_info_factory().id,
    }
    url = reverse("basket-detail", kwargs={'pk': order_item.id})

    # for AUTHORIZED owner client
    resp = client.patch(url, payload, format='json')
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert resp_json['product_info']['id'] == payload['product_info_id']


@pytest.mark.django_db
def test__update_quantity_basket_item_for_owner_client(api_client, product_info_factory, order_item_factory,
                                                       order_factory):
    # arrange
    client, owner = api_client()
    order = order_factory(owner=owner)
    order_item = order_item_factory(order=order)
    payload = {
        'quantity': 2
    }
    url = reverse("basket-detail", kwargs={'pk': order_item.id})

    # for AUTHORIZED owner client
    resp = client.patch(url, payload, format='json')
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert resp_json['quantity'] == payload['quantity']


@pytest.mark.django_db
def test_delete_basket_item_for_unauthorized_client(api_client, order_item_factory):
    # arrange
    client, owner = api_client(is_auth=False)
    order_item = order_item_factory()

    # UNAUTHORIZED
    url = reverse("basket-detail", kwargs={'pk': order_item.id})
    resp = client.delete(url)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    print(resp.rendered_content)


@pytest.mark.django_db
def test_delete_basket_item_for_not_owner_client(api_client, order_item_factory):
    # arrange
    client, owner = api_client()
    order_item = order_item_factory()

    # NOT OWNER
    url = reverse("basket-detail", kwargs={'pk': order_item.id})
    resp = client.delete(url)
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    print(resp.rendered_content)


@pytest.mark.django_db
def test_delete_basket_item_for_admin_client(api_client, order_item_factory, order_factory):
    # arrange
    # Если админ не покупатель
    client, _ = api_client(is_staff=True)
    order_item = order_item_factory()

    # Admin
    url = reverse("basket-detail", kwargs={'pk': order_item.id})
    resp = client.delete(url)
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    print(resp.rendered_content)


@pytest.mark.django_db
def test_delete_basket_item_for_owner_client(api_client, order_item_factory, order_factory):
    # arrange
    client, owner = api_client()
    order = order_factory(owner=owner)
    order_item = order_item_factory(order=order)

    # owner
    url = reverse("basket-detail", kwargs={'pk': order_item.id})
    resp = client.delete(url)
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    print(resp.rendered_content)


@pytest.mark.django_db
def test_confirm_basket_item_for_unauthorized_client(api_client):
    # arrange
    client, _ = api_client(is_auth=False)

    # unauthorized
    url = reverse("basket-confirm")
    resp = client.post(url)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    print(resp.rendered_content)


@pytest.mark.django_db
def test_confirm_basket_item_for_admin_client(api_client):
    # arrange
    # Админ как покупатель но с пустой корзиной
    client, _ = api_client(is_staff=True)

    # Admin
    url = reverse("basket-confirm")
    resp = client.patch(url)
    assert resp.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    print(resp.rendered_content)


@pytest.mark.django_db
def test_confirm_basket_item_for_not_owner_client(api_client):
    # arrange
    # Не владелец с пустой корзиной
    client, _ = api_client()

    # not owner
    url = reverse("basket-confirm")
    resp = client.patch(url)
    assert resp.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    print(resp.rendered_content)


@pytest.mark.django_db
def test_confirm_basket_item_for_owner_client(api_client, order_factory, order_item_factory):
    # arrange
    client, owner = api_client()
    order = order_factory(owner=owner)
    order_item_factory(order=order, _quantity=2)

    # owner
    url = reverse("basket-confirm")
    resp = client.patch(url)
    assert resp.status_code == status.HTTP_200_OK
    print(resp.rendered_content)
