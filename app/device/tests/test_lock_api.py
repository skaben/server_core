import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Lock
from device.serializers import LockSerializer

from tools_testing.assembly.device import device_assembly

LOCK_URL = reverse('api:lock-list')


class TestPublicLocksApi(APITestCase):
    """Test the publicly available locks API"""

    def test_login_required(self):
        """Test that login required for retrieving tags"""
        res = self.client.get(LOCK_URL)

        assert res.status_code == status.HTTP_401_UNAUTHORIZED


class TestPrivateLocksApi(APITestCase):
    """ Test private available locks API

        pytest fixtures is full of eels, using old x-unit format -_-
    """

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'password1234'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_locks(self):
        """ Test retrieving locks success. """
        for x in range(3):
            lock = device_assembly('lock')
            Lock.objects.create(uid=lock.uid,
                                ip=lock.ip)

        res = self.client.get(LOCK_URL)

        locks = Lock.objects.all()
        serializer = LockSerializer(locks, many=True)

        assert res.status_code == status.HTTP_200_OK
        assert res.data == serializer.data

    def test_create_lock_success(self):
        """ Test creating a new Lock success. """
        lock = device_assembly('lock')
        self.client.post(LOCK_URL, lock.get_payload())

        exists = Lock.objects.filter(ip=lock.ip).exists()

        assert exists

    def test_delete_lock_success(self):
        """ Test deleting a lock successm """
        lock = device_assembly('lock')
        self.client.post(LOCK_URL, lock.get_payload())
        present = Lock.objects.get(uid=lock.uid)
        res = self.client.delete(LOCK_URL + str(present.id) + '/')

        assert res.status_code in (status.HTTP_204_NO_CONTENT,
                                   status.HTTP_200_OK,
                                   status.HTTP_202_ACCEPTED)

    def test_patch_lock(self):
        """ Test partially updating lock successm """
        lock = device_assembly('lock')
        post_res = self.client.post(LOCK_URL, lock.get_payload())
        lock_id = str(post_res.data['id'])
        instance_url = LOCK_URL + lock_id + '/'
        new_descr = 'new' + lock.descr
        patch_res = self.client.patch(instance_url, {'descr': new_descr})
        patched = Lock.objects.get(id=lock_id)

        assert patch_res.status_code == status.HTTP_200_OK
        assert patched.descr == new_descr

    @pytest.mark.skip(reason='didn\'t decide about UPDATE option yet')
    def test_update_lock(self):
        """ Test fully updating lock success. """
        lock = device_assembly('lock')
        post_res = self.client.post(LOCK_URL, lock.get_payload())
        lock_id = str(post_res.data['id'])
        instance_url = LOCK_URL + lock_id + '/'
        new_payload = device_assembly('lock').get_payload()
        print(instance_url, new_payload)  # linter
