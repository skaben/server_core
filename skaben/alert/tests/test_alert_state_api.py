from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from core.models import AlertState, AlertCounter
from alert.serializers import AlertStateSerializer


API_URL = reverse('api:alertstate-list')


class TestPublicAlertApi(APITestCase):
    """Test the publicly available locks API"""

    def test_login_required(self):
        """Test that login required for retrieving tags"""
        res = self.client.get(API_URL)

        assert res.status_code == status.HTTP_401_UNAUTHORIZED


class TestPrivateAlertStateApi(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'testalert@test.com',
            'passwordmega123'
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_alert_states(self):
        for x in range(2):
            AlertState.objects.create(name=f'test_state_{x}',
                                      info='notimportant',
                                      current=False
                                      )
        res = self.client.get(API_URL)
        states = AlertState.objects.all()
        serializer = AlertStateSerializer(states, many=True)

        assert res.status_code == status.HTTP_200_OK
        assert res.data == serializer.data

    def test_alert_state_set_current_solitude(self):
        """ Test action set_current for solitude alert state
            without any other AlertState objects
        """
        state = AlertState.objects.create(name='statename',
                                          info='testinfo',
                                          current=False)
        instance_url = f'{API_URL}{str(state.id)}/set_current/'
        res = self.client.post(instance_url)

        patched = AlertState.objects.get(id=state.id)

        assert res.status_code == status.HTTP_200_OK, res.data
        assert patched.info == state.info, 'state change expected'

    def test_alert_state_set_current_normal(self):
        """ Test action set_current for alert state"""
        old = AlertState.objects.create(name='stateold',
                                        info='test2',
                                        current=True)
        new = AlertState.objects.create(name='statenew',
                                        info='test',
                                        current=False)
        counter = AlertCounter.objects.create(value='100500',
                                              comment='test')

        instance_url = f'{API_URL}{str(new.id)}/set_current/'
        res = self.client.post(instance_url)

        new_current = AlertState.objects.get(id=new.id)
        old_current = AlertState.objects.get(id=old.id)

        counter_new = AlertCounter.objects.latest('id')

        assert res.status_code == status.HTTP_200_OK
        assert old_current.current is False, 'change to False expected'
        assert new_current.current is True, 'change to True expected'
        assert counter_new.id != counter.id, 'counter create expected'

    def test_create_alert_state_fail(self):
        """ Test create new alert state via API fails """
        name = 'notastate'
        payload = {'name': name,
                   'current': True}
        res = self.client.post(API_URL, payload)
        exists = AlertState.objects.filter(name=name).exists()

        assert not exists
        assert res.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_update_alert_state_fail(self):
        """ Test partial update existing alert state fails """
        state = AlertState.objects.create(name='statename',
                                          info='testinfo',
                                          current=False)
        payload = {'current': True, 'name': '12345'}
        instance_url = API_URL + str(state.id) + '/'
        res = self.client.patch(instance_url, payload)

        assert res.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_delete_alert_state_fail(self):
        """ Test delete alert state via API fails """
        state = AlertState.objects.create(name='test')
        instance_url = API_URL + str(state.id) + '/'
        res = self.client.delete(instance_url)
        exists = AlertState.objects.filter(id=state.id).exists()

        assert exists
        assert res.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
