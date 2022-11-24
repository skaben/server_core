import logging
from core.helpers import get_server_time
from kombu import Message
from core.transport.handlers import BaseHandler
from core.transport.publish import get_interface
from core.transport.config import SkabenQueue
from core.devices import get_device_config
from skabenproto import CUP

__all__ = ['ClientUpdateHandler']

devices = get_device_config()
ext_publisher = get_interface()  # reusable interface for sending MQTT packets


class ClientUpdateHandler(BaseHandler):

    supported_op_types = [
        'force'
    ]
    incoming_mark = SkabenQueue.CLIENT_UPDATE.value

    def handle_message(self, body: dict, message: Message):
        [
            incoming_mark,
            device_type,
            device_uid,
        ] = message.delivery_info.get('routing_key').split('.')
        if incoming_mark != self.incoming_mark:
            message.requeue()
            return

        device = devices.get_by_topic(device_type)
        try:
            instance_data = self.get_instance_data(device, device_uid)
        except device.model.DoesNotExist:
            # todo: operation of new device approval is not implemented yet
            logging.error(f'device of type {device_type} with MAC {device_uid} not found in DB')
            return message.reject()
        message.ack()
        if instance_data.get('hash', 0) != body.get('hash', 1) \
                or message.headers.get('update_type') == 'force':
            packet = CUP(
                topic=device_type,
                uid=device_uid,
                task_id='n/a',
                datahold=instance_data,
                timestamp=get_server_time()
            )
            ext_publisher.send_mqtt_skaben(packet)

        self.update_timestamp_only(
            self.get_routing_key([SkabenQueue.STATE_UPDATE, device_type, device_uid])
        )

    @staticmethod
    def get_instance_data(device, mac_id):
        instance = device.model.objects.get(mac_addr=mac_id)
        serializer = device.serializer(instance=instance)
        return serializer.data

    def update_timestamp_only(self, routing_key: str, timestamp: int | None = None):
        timestamp = timestamp or get_server_time()
        self.producer.publish(
            {'timestamp': timestamp},
            exchange=self.config.internal_exchange,
            routing_key=routing_key
        )

