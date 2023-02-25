import pytest
from alert.serializers import AlertCounterSerializer
from core.models import AlertCounter, AlertState
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

API_URL = reverse('api:alertcounter-list')


class TestPublicAlertCounterApi(APITestCase):
    """Test the publicly available alert counter API"""

    def test_login_required(self):
        """Test that login required for retrieving tags"""
        res = self.client.get(API_URL)

        assert res.status_code == status.HTTP_401_UNAUTHORIZED


class TestPrivateAlertCounterApi(APITestCase):
    """ Test the private available alert counter API """

    # todo: border values tests, parametrization

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'testalert@test.com',
            'passwordmega123'
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_alert_counters(self):
        for x in range(1, 4):
            AlertCounter.objects.create(value=x, comment='notimportant')
        res = self.client.get(API_URL)
        states = AlertCounter.objects.all()
        serializer = AlertCounterSerializer(states, many=True)

        assert res.status_code == status.HTTP_200_OK, res.data
        assert res.data == serializer.data

    @pytest.mark.skip
    def test_create_alert_counter_state_switch(self):
        """ Test create alert counter with alert state switching """
        threshold = 100
        old_state = AlertState.objects.create(name='old_state',
                                              info='infoiption',
                                              threshold=1,
                                              current=True)
        switch = AlertState.objects.create(name='alert_switch',
                                           info='test',
                                           threshold=threshold,
                                           current=False)
        # alert_switch threshold range is now (threshold, 1000)
        # trying to create new counter
        new_cnt = self.client.post(API_URL, {'value': threshold,
                                             'comment': 'test'})

        # after creation of new_counter current state should be changed
        assert new_cnt.status_code == status.HTTP_201_CREATED, new_cnt.data

        old = AlertState.objects.get(pk=old_state.id)
        new = AlertState.objects.get(pk=switch.id)

        assert old.current is False, 'change to False expected'
        assert new.current is True, 'change to True expected'

    def test_create_alert_counter_state_no_switch(self):
        """ Test create alert counter without alert state switching """
        threshold = 100
        AlertState.objects.create(name='old_state_2',
                                  info='info',
                                  threshold=-1,
                                  current=True)
        switch = AlertState.objects.create(name='alert_switch_2',
                                           info='test',
                                           threshold=threshold,
                                           current=False)

        new_cnt = self.client.post(API_URL, {'value': threshold,
                                             'comment': 'test'})
        new = AlertState.objects.get(pk=switch.id)

        assert new_cnt.status_code == status.HTTP_201_CREATED, new_cnt.data
        assert new.current is False, 'change from False unexpected'
