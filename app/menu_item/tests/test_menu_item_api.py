from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from core.models import MenuItem
from menu_item.serializers import MenuItemSerializer
from tools_testing.assembly.ingame import ingame_assembly

MI_URL = reverse('api:menuitem-list')


class TestPublicMenuItemsApi(APITestCase):
    """Test the publicly available menu items PI"""

    def test_login_required(self):
        """Test that login required for retrieving items"""
        res = self.client.get(MI_URL)

        assert res.status_code == status.HTTP_401_UNAUTHORIZED


class TestPrivateMenuItemsAPI(APITestCase):
    """Test the private available menu items"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'password1234'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_menu_items(self):
        """ Test retrieving menu items success. """
        payload = ingame_assembly('menu').get_payload()
        for x in range(3):
            MenuItem.objects.create(**payload)

        res = self.client.get(MI_URL)

        items = MenuItem.objects.all()
        serializer = MenuItemSerializer(items, many=True)

        assert res.status_code == status.HTTP_200_OK, res.content
        assert res.data == serializer.data, serializer.data

    def test_create_menu_item(self):
        """ Test create menu item """
        item = ingame_assembly('menu')
        res = self.client.post(MI_URL, item.payload)

        exists = MenuItem.objects.filter(action=item.action).exists()

        assert res.status_code == status.HTTP_201_CREATED, res.content
        assert exists, 'item not in database'
