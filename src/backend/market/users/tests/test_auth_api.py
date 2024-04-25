import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from products.models import Shop


@pytest.mark.django_db
class TestAuth:

    USERNAME = 'person'
    PASS = 'eu2398e928'
    EMAIL = 'person1@world.com'
    NEW_PASS = 'eu2398e928'

    REGISTRATION_DATA = {
        'email': EMAIL,
        'password1': PASS,
        'password2': PASS,
    }

    client = APIClient()
    login_url = reverse('rest_login')
    logout_url = reverse('rest_logout')
    password_change_url = reverse('rest_password_change')
    register_url = reverse('rest_register')
    password_reset_url = reverse('rest_password_reset')
    user_url = reverse('rest_user_details')
    verify_email_url = reverse('rest_verify_email')
    resend_email_url = reverse("rest_resend_email")
    #
    # def _login(self):
    #     payload = {
    #         'username': self.USERNAME,
    #         'password': self.PASS,
    #     }
    #     self.post(self.login_url, data=payload, status_code=status.HTTP_200_OK)
    #
    # def _logout(self):
    #     self.post(self.logout_url, status=status.HTTP_200_OK)

    def test_validate_simple_password(self):
        # arrange
        payload = {
            'email': self.EMAIL,
            'password1': '11',
            'password2': '11'
        }

        # for UNAUTHORIZED client
        resp = self.client.post(self.register_url, payload, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        print(resp.rendered_content)

    def test_register_failed_email_validation(self):
        # arrange
        payload = {
            'email': '',
            'password1': self.PASS,
            'password2': self.PASS
        }

        # for UNAUTHORIZED client
        resp = self.client.post(self.register_url, payload, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        print(resp.rendered_content)

    def test_register_with_non_unique_email_validation(self):
        # register user
        self.client.post(self.register_url, self.REGISTRATION_DATA, format='json')

        # register with same email
        resp = self.client.post(self.register_url, self.REGISTRATION_DATA, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        print(resp.json())

    def test_register(self, api_client):
        resp = self.client.post(self.register_url, self.REGISTRATION_DATA, format='json')
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.json().get('key')
        print(resp.json())

    def test_register_is_supplier(self, api_client):
        payload = {
            **self.REGISTRATION_DATA,
            'is_supplier': True
        }
        resp = self.client.post(self.register_url, payload, format='json')
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.json().get('key')
        print(resp.json())
        shops = list(Shop.objects.all())
        assert shops


    # def test_verify_email(self, api_client):
    #     # register
    #     resp = self.client.post(self.register_url, self.REGISTRATION_DATA, format='json')
    #     key = resp.json()['key']
    #     payload = {
    #         'email': self.REGISTRATION_DATA['email'],
    #         'key': key
    #     }
    #     # confirm email
    #     resp = self.client.post(self.verify_email_url, payload, format='json')
    #     assert resp.status_code == status.HTTP_200_OK
    #     print(resp.json())
    #
    # def test_login_user(self, api_client):
    #     client, user = api_client(is_auth=False)
    #     # register
    #     resp = client.post(self.url_register, self.payload, format='json')
    #     email = resp.json()['email']
    #     # confirm email
    #     token = ConfirmEmailToken.objects.filter(user__email=email).first()
    #     assert token
    #     payload = {
    #         'email': email,
    #         'confirm_token': token.key
    #     }
    #     client.post(self.url_confirm, payload, format='json')
    #     # user login
    #     resp = client.post(self.url_login, self.payload, format='json')
    #     print(resp.rendered_content)
    #     assert resp.status_code == status.HTTP_200_OK
    #     assert resp.json()['token']
    #
    # def test_logout_user(self, api_client):
    #     # user already confirm email - is_active=True
    #     client, user = api_client()
    #     resp = client.post(self.url_logout, format='json')
    #     assert resp.status_code == status.HTTP_200_OK
    #     resp = client.post(self.url_logout, format='json')
    #     assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    #
    #
    #
