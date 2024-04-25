from dj_rest_auth.tests.mixins import APIClient
from rest_framework import status
from rest_framework.reverse import reverse


def test_health():
    api_client = APIClient()
    url = reverse("health-check")
    resp = api_client.get(url)
    assert resp.status_code == status.HTTP_200_OK
