import os

import pytest
from django.conf import settings
from rest_framework import status
from rest_framework.reverse import reverse


@pytest.mark.django_db
def test_shop_import_data_for_unauthorized(api_client, shop_factory):
    # arrange
    client, user = api_client(is_auth=False)
    shop = shop_factory()
    url = reverse("shops-import-data", kwargs={'pk': shop.id})
    resp = client.put(url, content_type='application/yaml')

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_shop_import_data_for_non_supplier(api_client, shop_factory):
    # arrange
    client, user = api_client()
    shop = shop_factory()
    url = reverse("shops-import-data", kwargs={'pk': shop.id})
    resp = client.put(url, content_type='application/yaml')

    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_shop_import_data_for_supplier_not_owner(api_client, shop_factory):
    # arrange
    client, user = api_client(is_supplier=True)
    shop = shop_factory()
    url = reverse("shops-import-data", kwargs={'pk': shop.id})
    resp = client.put(url, content_type='application/yaml')

    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_shop_import_data_for_supplier(api_client, shop_factory):
    # arrange
    client, user = api_client(is_supplier=True)
    url = reverse("shops-import-data", kwargs={'pk': user.shop.id})
    file_path = os.path.join(settings.BASE_DIR, 'tests', 'backend_app', 'shop1.yaml')
    with open(file_path, "r", encoding='utf-8') as f:
        resp = client.put(url, f.read(), content_type='application/yaml')

    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_shop_import_data_for_supplier(api_client, shop_factory):
    # arrange
    client, user = api_client(is_staff=True)
    shop = shop_factory()
    url = reverse("shops-import-data", kwargs={'pk': shop.id})
    file_path = os.path.join(settings.BASE_DIR, 'tests', 'backend_app', 'shop1.yaml')
    with open(file_path, "r", encoding='utf-8') as f:
        resp = client.put(url, f.read(), content_type='application/yaml')

    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_export_shop_data_permissions(api_client, shop_factory):
    # arrange
    client_supplier, user_supplier = api_client(is_supplier=True)
    # import
    url = reverse("shops-import-data", kwargs={'pk': user_supplier.shop.id})
    file_path = os.path.join(settings.BASE_DIR, 'tests', 'backend_app', 'shop1.yaml')
    with open(file_path, "r", encoding='utf-8') as f:
        resp = client_supplier.put(url, f.read(), content_type='application/yaml')

    assert resp.status_code == status.HTTP_200_OK

    shop = shop_factory()
    # export
    # unauthorized
    client, user = api_client(is_auth=False)
    url = reverse("shops-export-data", kwargs={'pk': shop.id})
    resp = client.get(url)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    # for non supplier
    client, user = api_client()
    url = reverse("shops-export-data", kwargs={'pk': shop.id})
    resp = client.get(url)
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # for supplier not owner
    client, user = api_client(is_supplier=True)
    url = reverse("shops-export-data", kwargs={'pk': shop.id})
    resp = client.get(url)
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    # for supplier owner
    url = reverse("shops-export-data", kwargs={'pk': user_supplier.shop.id})
    resp = client_supplier.get(url)
    assert resp.status_code == status.HTTP_200_OK

    # for admin
    client, user = api_client(is_staff=True)
    url = reverse("shops-export-data", kwargs={'pk': shop.id})
    resp = client.get(url)
    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_import_export_shop_data(api_client):
    # arrange
    client, user = api_client(is_supplier=True)
    url = reverse("shops-import-data", kwargs={'pk': user.shop.id})
    file_path = os.path.join(settings.BASE_DIR, 'tests', 'backend_app', 'shop1.yaml')
    with open(file_path, "r", encoding='utf-8') as f:
        resp = client.put(url, f.read(), content_type='application/yaml')

    assert resp.status_code == status.HTTP_200_OK

    url = reverse("shops-export-data", kwargs={'pk': user.shop.id})
    resp = client.get(url)
    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_retrieve_shop_for_unauthorized_client(shop_factory, api_client):
    # arrange
    client, _ = api_client(is_auth=False)
    instance = shop_factory()
    url = reverse("shops-detail", kwargs={'pk': instance.id})

    # for UNAUTHORIZED client
    resp = client.get(url)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_list_shops_for_unauthorized_client(api_client):
    # arrange
    client, _ = api_client(is_auth=False)
    url = reverse("shops-list")

    # for UNAUTHORIZED client
    resp = client.get(url)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_list_shops_for_authorized_client(api_client, shop_factory):
    # arrange
    client, _ = api_client()
    instances = shop_factory(_quantity=10)
    url = reverse("shops-list")

    # for Auth client
    resp = client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert resp_json['count'] == len(instances)


@pytest.mark.django_db
def test_create_shop_for_unauthorized_client(api_client):
    # arrange
    client, _ = api_client(is_auth=False)
    payload = {
        'name': 'test'
    }
    url = reverse("shops-list")

    # for UNAUTHORIZED client
    resp = client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_create_shop_for_non_supplier_and_non_admin(api_client):
    client, _ = api_client()
    payload = {
        'name': 'test'
    }
    # auth user create
    url = reverse("shops-list")
    resp = client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_create_shop_for_admin_client(api_client):
    client, _ = api_client(is_staff=True)

    payload = {
        'name': 'test',
    }
    # admin create
    url = reverse("shops-list")
    resp = client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_create_shop_for_supplier_client(api_client, shop_factory):
    client, _ = api_client(is_supplier=True)
    payload = {
        'name': 'test',
    }
    # supplier create
    url = reverse("shops-list")
    resp = client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_shop_for_unauthorized_client(api_client, shop_factory):
    # arrange
    client, _ = api_client(is_auth=False)
    shop = shop_factory()
    payload = {
        'name': 'test'
    }
    url = reverse("shops-detail", kwargs={'pk': shop.id})

    # for UNAUTHORIZED client
    resp = client.patch(url, payload, format='json')
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_update_shop_for_non_supplier_and_non_admin(api_client, shop_factory):
    client, _ = api_client()
    shop = shop_factory()
    payload = {
        'name': 'test'
    }
    # auth user update
    url = reverse("shops-detail", kwargs={'pk': shop.id})
    resp = client.patch(url, payload, format='json')
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_shop_for_admin_client(api_client, shop_factory):
    client, _ = api_client(is_staff=True)
    shop = shop_factory()
    payload = {
        'name': 'test',
    }
    # admin update
    url = reverse("shops-detail", kwargs={'pk': shop.id})
    resp = client.patch(url, payload, format='json')
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_shop_for_supplier_not_owner_client(api_client, shop_factory):
    client, _ = api_client(is_supplier=True)
    shop = shop_factory()
    payload = {
        'name': 'test',
    }
    # supplier update
    url = reverse("shops-detail", kwargs={'pk': shop.id})
    resp = client.patch(url, payload, format='json')
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_shop_for_supplier_owner_client(api_client, shop_factory):
    client, user = api_client(is_supplier=True)
    shop = user.shop
    payload = {
        'name': 'test',
    }
    # supplier update
    url = reverse("shops-detail", kwargs={'pk': shop.id})
    resp = client.patch(url, payload, format='json')
    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_delete_shop_for_unauthorized_client(api_client, shop_factory):
    client, _ = api_client(is_auth=False)
    shop = shop_factory()
    # admin delete
    url = reverse("shops-detail", kwargs={'pk': shop.id})
    resp = client.delete(url, format='json')
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_delete_shop_for_auth_client(api_client, shop_factory):
    client, _ = api_client()
    shop = shop_factory()
    # auth delete
    url = reverse("shops-detail", kwargs={'pk': shop.id})
    resp = client.delete(url, format='json')
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_shop_for_supplier_client(api_client, shop_factory):
    client, user = api_client(is_supplier=True)
    shop = user.shop
    # supplier delete
    url = reverse("shops-detail", kwargs={'pk': shop.id})
    resp = client.delete(url, format='json')
    assert resp.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_delete_shop_for_admin_client(api_client, shop_factory):
    client, _ = api_client(is_staff=True)
    shop = shop_factory()
    # admin delete
    url = reverse("shops-detail", kwargs={'pk': shop.id})
    resp = client.delete(url, format='json')
    assert resp.status_code == status.HTTP_204_NO_CONTENT
