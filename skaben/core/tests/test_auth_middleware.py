from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from testing.helpers import create_user

ROOT_URL = '/'
AUTH_URL = reverse('token')


class TestAuthMiddlewareNotAuthenticated(APITestCase):
    """Test the publicly available locks API"""

    def test_login_required(self):
        """Test that login required for retrieving tags"""
        res = self.client.get(ROOT_URL)

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_url_accessible(self):
        """ Test that token url is accessible without authorization """
        res = self.client.get(AUTH_URL)

        assert res.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_token_authorization_success(self):
        """ Test that client receives authorization token success """
        payload = {'username': 'test',
                   'password': 'testing'}
        create_user(**payload)

        res = self.client.post(AUTH_URL, payload)

        assert res.status_code == status.HTTP_200_OK

    def test_token_authorization_fail(self):
        """ Test that client receives authorization token fail """
        payload = {'username': 'test',
                   'password': 'testing'}

        res = self.client.post(AUTH_URL, payload)

        assert res.status_code == status.HTTP_400_BAD_REQUEST
