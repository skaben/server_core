import pytest
from unittest.mock import Mock
from core.transport.config import MQConfig, SkabenQueue
from mymodule import ClientUpdateHandler


class TestClientUpdateHandler:
    
    def test_get_instance_data(self):
        # create a mock device and instance
        mock_device = Mock()
        mock_instance = Mock()
        mock_device.model.objects.get.return_value = mock_instance

        # create a mock serializer and data
        mock_serializer = Mock()
        mock_data = {'foo': 'bar'}
        mock_serializer.data = mock_data
        mock_device.serializer.return_value = mock_serializer

        # call the get_instance_data method with the mock arguments
        instance_data = ClientUpdateHandler.get_instance_data(mock_device, 'mac_id')

        # assert that the mock serializer was called with the mock instance and that the method returned the expected data
        mock_device.model.objects.get.assert_called_once_with(mac_addr='mac_id')
        mock_device.serializer.assert_called_once_with(instance=mock_instance)
        assert instance_data == mock_data

    def test_handle_message(self):
        config = MQConfig(conn='connection_string')
        queues = {'myqueue': 'myexchange'}
        handler = ClientUpdateHandler(config, queues)

        # create a mock message and body
        mock_message = Mock()
        mock_body = {'foo': 'bar'}
        mock_message.delivery_info.get.return_value = {'routing_key': 'client_update.device_type.device_uid'}

        # call the handle_message method with the mock arguments
        handler.handle_message(mock_body, mock_message)

        # assert that the mock message was acked
        mock_message.ack.assert_called_once()