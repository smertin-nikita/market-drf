import pytest
from rest_framework import status
from rest_framework.reverse import reverse


@pytest.mark.django_db
def test_retrieve_parameter_for_unauthorized_client(parameter_factory, api_client):
    # arrange
    client, _ = api_client(is_auth=False)
    instance = parameter_factory()
    url = reverse("categories-detail", kwargs={'pk': instance.id})

    # for UNAUTHORIZED client
    resp = client.get(url)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_list_categories_for_unauthorized_client(api_client):
    # arrange
    client, _ = api_client(is_auth=False)
    url = reverse("categories-list")

    # for UNAUTHORIZED client
    resp = client.get(url)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_list_categories_for_authorized_client(api_client, category_factory):
    # arrange
    client, _ = api_client()
    instances = category_factory(_quantity=10)
    url = reverse("categories-list")

    # for Auth client
    resp = client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert resp_json['count'] == len(instances)


@pytest.mark.django_db
def test_create_parameter_for_unauthorized_client(api_client):
    # arrange
    client, _ = api_client(is_auth=False)
    payload = {
        'name': 'test'
    }
    url = reverse("categories-list")

    # for UNAUTHORIZED client
    resp = client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_create_parameter_for_non_supplier_and_non_admin(api_client):
    client, _ = api_client()
    payload = {
        'name': 'test'
    }
    # auth user create
    url = reverse("categories-list")
    resp = client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_create_parameter_for_admin_client(api_client):
    client, _ = api_client(is_staff=True)

    payload = {
        'name': 'test',
    }
    # admin create
    url = reverse("categories-list")
    resp = client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_201_CREATED
    resp_json = resp.json()
    assert len(resp_json) == 2  # fields count
    assert resp_json['name'] == payload['name']


@pytest.mark.django_db
def test_create_parameter_for_supplier_client(api_client, shop_factory):
    client, _ = api_client(is_supplier=True)
    payload = {
        'name': 'test',
    }
    # supplier create
    url = reverse("categories-list")
    resp = client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_201_CREATED
    resp_json = resp.json()
    assert len(resp_json) == 2   # fields count
    assert resp_json['name'] == payload['name']


@pytest.mark.django_db
def test_update_parameter_for_unauthorized_client(api_client, parameter_factory):
    # arrange
    client, _ = api_client(is_auth=False)
    parameter = parameter_factory()
    payload = {
        'name': 'test'
    }
    url = reverse("categories-detail", kwargs={'pk': parameter.id})

    # for UNAUTHORIZED client
    resp = client.patch(url, payload, format='json')
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_update_parameter_for_non_supplier_and_non_admin(api_client, parameter_factory):
    client, _ = api_client()
    parameter = parameter_factory()
    payload = {
        'name': 'test'
    }
    # auth user update
    url = reverse("categories-detail", kwargs={'pk': parameter.id})
    resp = client.patch(url, payload, format='json')
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_category_for_admin_client(api_client, category_factory):
    client, _ = api_client(is_staff=True)
    category = category_factory()
    payload = {
        'name': 'test',
    }
    # admin update
    url = reverse("categories-detail", kwargs={'pk': category.id})
    resp = client.patch(url, payload, format='json')
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert len(resp_json) == 2   # fields count
    assert resp_json['name'] == payload['name']


@pytest.mark.django_db
def test_update_parameter_for_supplier_client(api_client, parameter_factory):
    client, _ = api_client(is_supplier=True)
    parameter = parameter_factory()
    payload = {
        'name': 'test',
    }
    # supplier update
    url = reverse("categories-detail", kwargs={'pk': parameter.id})
    resp = client.patch(url, payload, format='json')
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_validate_empty_name_on_create_parameter_for_admin_client(api_client):
    client, _ = api_client(is_staff=True)

    payload = {}
    # admin create
    url = reverse("categories-list")
    resp = client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_delete_parameter_for_unauthorized_client(api_client, parameter_factory):
    client, _ = api_client(is_auth=False)
    parameter = parameter_factory()
    # admin delete
    url = reverse("categories-detail", kwargs={'pk': parameter.id})
    resp = client.delete(url, format='json')
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_delete_parameter_for_auth_client(api_client, parameter_factory):
    client, _ = api_client()
    parameter = parameter_factory()
    # auth delete
    url = reverse("categories-detail", kwargs={'pk': parameter.id})
    resp = client.delete(url, format='json')
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_parameter_for_supplier_client(api_client, parameter_factory):
    client, _ = api_client(is_supplier=True)
    parameter = parameter_factory()
    # supplier delete
    url = reverse("categories-detail", kwargs={'pk': parameter.id})
    resp = client.delete(url, format='json')
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_category_for_admin_client(api_client, category_factory):
    client, _ = api_client(is_staff=True)
    parameter = category_factory()
    # admin delete
    url = reverse("categories-detail", kwargs={'pk': parameter.id})
    resp = client.delete(url, format='json')
    assert resp.status_code == status.HTTP_204_NO_CONTENT
