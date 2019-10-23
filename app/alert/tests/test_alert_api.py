import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from core.models import AlertState
from alert.serializers import AlertStateSerializer


API_URL = reverse('api:alertstate-list')


class TestPublicAlertApi(APITestCase):
    """Test the publicly available locks API"""

    def test_login_required(self):
        """Test that login required for retrieving tags"""
        res = self.client.get(API_URL)

        assert res.status_code == status.HTTP_401_UNAUTHORIZED


class TestPrivateAlertApi(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'testalert@test.com',
            'passwordmega123'
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_alert_states(self):
        for x in range(2):
            AlertState.objects.create(name=f'test_state_{x}',
                                      descr='notimportant',
                                      current=False
                                      )
        res = self.client.get(API_URL)
        states = AlertState.objects.all()
        serializer = AlertStateSerializer(states, many=True)

        assert res.status_code == status.HTTP_200_OK
        assert res.data == serializer.data

    @pytest.mark.skip(reason='still horsing around partial update')
    def test_patch_alert_state_current_field(self):
        """ Test partial update existing alert state success. """
        state = AlertState.objects.create(name='statename',
                                          descr='testdescr',
                                          current=False)
        payload = {'current': True}
        instance_url = API_URL + str(state.id) + '/'
        res = self.client.patch(instance_url, payload)
        patched = AlertState.objects.get(id=state.id)

        assert state.current is False
        assert patched.current is True
        assert res.status_code == status.HTTP_200_OK

    @pytest.mark.skip(reason='still horsing around partial update')
    def test_patch_alert_state_not_current_field_fail(self):
        """ Test patch alert state any field other than current fails"""
        state = AlertState.objects.create(name='statename',
                                          descr='testdescr',
                                          current=False)
        payload = {'descr': 'any'}
        instance_url = API_URL + str(state.id) + '/'
        res = self.client.patch(instance_url, payload)
        patched = AlertState.objects.get(id=state.id)

        assert res.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert patched.descr == state.descr

    def test_create_alert_state_fail(self):
        """ Test create new alert state via API fails """
        name = 'notastate'
        payload = {'name': name,
                   'current': True}
        res = self.client.post(API_URL, payload)
        exists = AlertState.objects.filter(name=name).exists()

        assert res.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert not exists

    def test_delete_alert_state_fail(self):
        """ Test delete alert state via API fails """
        state = AlertState.objects.create(name='test')
        instance_url = API_URL + str(state.id) + '/'
        res = self.client.delete(instance_url)
        exists = AlertState.objects.filter(id=state.id).exists()

        assert exists
        assert res.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
