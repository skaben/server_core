from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Lock
from lock.serializers import LockSerializer

from test_factories import device_factory

LOCK_URL = reverse('lock:lock-list')


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
        """ Test retrieving locks """
        for x in range(3):
            lock = device_factory('lock')
            Lock.objects.create(uid=lock.uid,
                                ip=lock.ip)

        res = self.client.get(LOCK_URL)

        locks = Lock.objects.all()
        serializer = LockSerializer(locks, many=True)

        assert res.status_code == status.HTTP_200_OK
        assert res.data == serializer.data

    def test_create_lock_default_successfull(self):
        """ Test creating a new Lock """
        lock = device_factory('lock')
        self.client.post(LOCK_URL, lock.get_payload())

        exists = Lock.objects.filter(ip=lock.ip).exists()

        assert exists

    def test_delete_lock(self):
        lock = device_factory('lock')
        self.client.post(LOCK_URL, lock.get_payload())
        present = Lock.objects.get(uid=lock.uid)
        URL = LOCK_URL + str(present.id) + '/'
        res = self.client.delete(URL)

        assert res.status_code in (status.HTTP_204_NO_CONTENT,
                                   status.HTTP_200_OK,
                                   status.HTTP_202_ACCEPTED)
