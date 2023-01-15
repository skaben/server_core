from core.helpers import get_server_time
from kombu import Message
from core.transport.config import SkabenQueue
from core.transport.queue_handlers import BaseHandler
from core.devices import get_device_config

__all__ = ['StateUpdateHandler']

devices = get_device_config()


class StateUpdateHandler(BaseHandler):

    # making serializer know that we don't need to send updated config back to device
    context: dict = {
        'no_send': True
    }
    incoming_marks = SkabenQueue.STATE_UPDATE.value

    def handle_message(self, body: dict, message: Message):
        (
            incoming_mark,
            device_type,
            device_uid,
            packet_type
        ) = message.delivery_info.get('routing_key').split('.')
        if incoming_mark != self.incoming_mark:
            message.requeue()
            return

        message.ack()

        if packet_type == 'sup':
            self.save_device_state(device_type, device_uid, body)


    def save_device_state(self, device_type: str, device_uid: str, data: dict):
        device = devices.get_by_topic(device_type)
        serialized = device.schema(device.model.objects.get(uid=device_uid),
                                   context=self.context,
                                   data=data,
                                   partial=True)
        if serialized.is_valid():
            serialized.save()
