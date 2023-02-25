import pytest
from core.models import MenuItem, Terminal
from peripheral_devices.serializers import TerminalSerializer
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from testing.assembly.device import device_assembly
from testing.assembly.ingame import ingame_assembly

TERMINAL_URL = reverse('api:terminal-list')


class TestPublicTerminalsApi(APITestCase):
    """Test the publicly available terminals API"""

    def test_login_required(self):
        """Test that login required for retrieving tags"""
        res = self.client.get(TERMINAL_URL)

        assert res.status_code == status.HTTP_401_UNAUTHORIZED


#@pytest.mark.skip(reason='menuitem api not implemented yet')
class TestPrivateTerminalsApi(APITestCase):
    """ Test private available terminals API

        pytest fixtures is full of eels, using old x-unit format -_-
    """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'password1234'
        )
        self.client.force_authenticate(self.user)
        for x in range(3):
            item = ingame_assembly('menu')
            MenuItem.objects.create(**item.payload)
        self.items = list(MenuItem.objects.all())

    def test_retrieve_terminals(self):
        """ Test retrieving terminals success. """
        for x in range(3):
            device = device_assembly('terminal')
            Terminal.objects.create(**device.get_payload(('uid', 'ip')))

        res = self.client.get(TERMINAL_URL)

        terminals = Terminal.objects.all()
        serializer = TerminalSerializer(terminals, many=True)

        assert res.status_code == status.HTTP_200_OK
        assert res.data == serializer.data

    def test_create_terminal_success(self):
        """ Test creating a new Terminal success. """
        device = device_assembly('terminal', menu_items=self.items)
        res = self.client.post(TERMINAL_URL, device.payload)

        exists = Terminal.objects.filter(ip=device.ip).exists()

        assert res.status_code == status.HTTP_200_OK, res.content
        assert exists

    def test_delete_terminal_success(self):
        """ Test deleting a terminal successm """
        device = device_assembly('terminal')
        self.client.post(TERMINAL_URL, device.get_payload())
        present = Terminal.objects.get(uid=device.uid)
        res = self.client.delete(TERMINAL_URL + str(present.id) + '/')

        assert res.status_code in (status.HTTP_204_NO_CONTENT,
                                   status.HTTP_200_OK,
                                   status.HTTP_202_ACCEPTED)

    def test_patch_terminal(self):
        """ Test partially updating terminal successm """
        device = device_assembly('terminal')
        post_res = self.client.post(TERMINAL_URL, device.get_payload())
        terminal_id = str(post_res.data['id'])
        instance_url = TERMINAL_URL + terminal_id + '/'
        new_descr = 'new terminal descr'
        patch_res = self.client.patch(instance_url, {'descr': new_descr})
        patched = Terminal.objects.get(id=device.id)

        assert patch_res.status_code == status.HTTP_200_OK
        assert patched.descr == new_descr

    @pytest.mark.skip(reason='didn\'t decide about UPDATE option yet')
    def test_update_terminal(self):
        """ Test fully updating terminal success. """
        device = device_assembly('terminal')
        post_res = self.client.post(TERMINAL_URL, device.get_payload())
        terminal_id = str(post_res.data['id'])
        instance_url = TERMINAL_URL + terminal_id + '/'
        new_payload = device_assembly('terminal').get_payload()
        print(instance_url, new_payload)  # linter
