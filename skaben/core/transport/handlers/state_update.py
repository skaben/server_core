from core.helpers import get_server_time
from kombu import Message
from core.transport.config import SkabenQueue
from core.transport.handlers import BaseHandler
from core.devices import get_device_config

__all__ = ['StateUpdateHandler']

devices = get_device_config()


class StateUpdateHandler(BaseHandler):

    # making serializer know that we don't need to send updated config back to device
    context: dict = {
        'no_send': True
    }
    incoming_mark = SkabenQueue.STATE_UPDATE.value

    def handle_message(self, body: dict, message: Message):
        (
            incoming_mark,
            device_type,
            device_uuid,
            packet_type
        ) = message.delivery_info.get('routing_key').split('.')
        if incoming_mark != self.incoming_mark:
            message.requeue()
            return

        message.ack()
        device = devices.get_by_topic(device_type)
        serialized = device.schema(self.get_instance(device.model, device_uuid),
                                   context=self.context,
                                   data=body,
                                   partial=True)
        if serialized.is_valid():
            serialized.save()

    @staticmethod
    def get_instance(model, uid):
        return model.objects.get(uid=uid)
