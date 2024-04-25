import pytest
from rest_framework import status
from rest_framework.reverse import reverse


@pytest.mark.django_db
def test_retrieve_product_for_unauthorized_client(product_factory, api_client):
    # arrange
    client, _ = api_client(is_auth=False)
    instance = product_factory()
    url = reverse("products-detail", kwargs={'pk': instance .id})

    # for UNAUTHORIZED client
    resp = client.get(url)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_retrieve_product_info(api_client, product_factory, product_info_factory, shop_factory):
    client, _ = api_client()
    product = product_factory()
    instances = product_info_factory(_quantity=3, product=product)
    # Auth client
    url = reverse("products-detailed", kwargs={'pk': product.id})
    resp = client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert len(resp_json) == len(instances)
    for i, item in enumerate(instances):
        assert resp_json[i]['code_id'] == item.code_id
        assert resp_json[i]['product']['name'] == item.product.name


@pytest.mark.django_db
def test_list_products_for_unauthorized_client(api_client):
    # arrange
    client, _ = api_client(is_auth=False)
    url = reverse("products-list")

    # for UNAUTHORIZED client
    resp = client.get(url)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_list_products_for_authorized_client(api_client, product_factory):
    # arrange
    client, _ = api_client()
    instances = product_factory(_quantity=10)
    url = reverse("products-list")

    # for Auth client
    resp = client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()['results']
    assert len(resp_json) == len(instances)


@pytest.mark.django_db
def test_filter_category_products(api_client, product_factory, category_factory):
    # arrange
    client, _ = api_client()
    instance = product_factory(category=category_factory())
    product_factory(_quantity=10)
    url = reverse("products-list")

    # for Auth client
    resp = client.get(url, {'category': instance.category_id})
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()['results']
    assert len(resp_json) == 1
    assert resp_json[0]['category'] == instance.category.name


@pytest.mark.django_db
def test_create_product_for_unauthorized_client(api_client):
    # arrange
    client, _ = api_client(is_auth=False)
    payload = {
        'name': 'test'
    }
    url = reverse("products-list")

    # for UNAUTHORIZED client
    resp = client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_create_product_for_non_supplier_and_non_admin(api_client):
    client, _ = api_client()
    payload = {
        'name': 'test'
    }
    # auth user create
    url = reverse("products-list")
    resp = client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_create_product_for_admin_client(api_client):
    client, _ = api_client(is_staff=True)

    payload = {
        'name': 'test',
    }
    # admin create
    url = reverse("products-list")
    resp = client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_201_CREATED
    resp_json = resp.json()
    assert len(resp_json) == 3   # fields count
    assert resp_json['name'] == payload['name']


@pytest.mark.django_db
def test_create_product_for_supplier_client(api_client, shop_factory):
    client, _ = api_client(is_supplier=True)
    payload = {
        'name': 'test',
    }
    # supplier create
    url = reverse("products-list")
    resp = client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_201_CREATED
    resp_json = resp.json()
    assert len(resp_json) == 3   # fields count
    assert resp_json['name'] == payload['name']


@pytest.mark.django_db
def test_update_product_for_unauthorized_client(api_client, product_factory):
    # arrange
    client, _ = api_client(is_auth=False)
    product = product_factory()
    payload = {
        'name': 'test'
    }
    url = reverse("products-detail", kwargs={'pk': product.id})

    # for UNAUTHORIZED client
    resp = client.patch(url, payload, format='json')
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_update_product_for_non_supplier_and_non_admin(api_client, product_factory):
    client, _ = api_client()
    product = product_factory()
    payload = {
        'name': 'test'
    }
    # auth user update
    url = reverse("products-detail", kwargs={'pk': product.id})
    resp = client.patch(url, payload, format='json')
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_update_product_for_admin_client(api_client, product_factory):
    client, _ = api_client(is_staff=True)
    product = product_factory()
    payload = {
        'name': 'test',
    }
    # admin update
    url = reverse("products-detail", kwargs={'pk': product.id})
    resp = client.patch(url, payload, format='json')
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert len(resp_json) == 3   # fields count
    assert resp_json['name'] == payload['name']


@pytest.mark.django_db
def test_update_product_for_supplier_client(api_client, product_factory):
    client, _ = api_client(is_supplier=True)
    product = product_factory()
    payload = {
        'name': 'test',
    }
    # supplier update
    url = reverse("products-detail", kwargs={'pk': product.id})
    resp = client.patch(url, payload, format='json')
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_validate_empty_name_on_create_product_for_admin_client(api_client):
    client, _ = api_client(is_staff=True)

    payload = {}
    # admin create
    url = reverse("products-list")
    resp = client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_delete_product_for_unauthorized_client(api_client, product_factory):
    client, _ = api_client(is_auth=False)
    product = product_factory()
    # admin delete
    url = reverse("products-detail", kwargs={'pk': product.id})
    resp = client.delete(url, format='json')
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_delete_product_for_auth_client(api_client, product_factory):
    client, _ = api_client()
    product = product_factory()
    # auth delete
    url = reverse("products-detail", kwargs={'pk': product.id})
    resp = client.delete(url, format='json')
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_product_for_supplier_client(api_client, product_factory):
    client, _ = api_client(is_supplier=True)
    product = product_factory()
    # supplier delete
    url = reverse("products-detail", kwargs={'pk': product.id})
    resp = client.delete(url, format='json')
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_delete_product_for_admin_client(api_client, product_factory):
    client, _ = api_client(is_staff=True)
    product = product_factory()
    # admin delete
    url = reverse("products-detail", kwargs={'pk': product.id})
    resp = client.delete(url, format='json')
    assert resp.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_retrieve_product_detailed_for_unauthorized_client(product_factory, api_client):
    # arrange
    client, _ = api_client(is_auth=False)
    product = product_factory()
    url = reverse("products-detailed", kwargs={'pk': product.id})

    # for UNAUTHORIZED client
    resp = client.get(url)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_retrieve_product_detailed_for_authorized_client(product_factory, api_client, product_info_factory):
    # arrange
    client, _ = api_client()
    product = product_factory()
    product_infos = product_info_factory(_quantity=5, product=product)
    url = reverse("products-detailed", kwargs={'pk': product.id})

    # for AUTHORIZED client
    resp = client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    for i, info in enumerate(product_infos):
        resp_json[i]['id'] = info.id

