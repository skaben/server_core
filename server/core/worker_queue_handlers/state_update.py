from typing import Dict

from core.devices import get_device_config
from core.transport.config import MQConfig, SkabenPackets, SkabenQueue
from core.worker_queue_handlers.base import BaseHandler
from kombu import Message


class StateUpdateHandler(BaseHandler):
    """
    Handler for state update messages.
    """
    name: str = 'state_update'
    context: Dict[str, bool] = {'no_send': True}
    incoming_mark: str = SkabenQueue.STATE_UPDATE.value

    def __init__(self, config: MQConfig, queues: Dict[str, str]):
        """
        Initializes the StateUpdateHandler.

        Args:
            config (MQConfig): The message queue configuration.
            queues (dict): The queues for the handler.
        """
        super().__init__(config, queues)

    def handle_message(self, body: Dict, message: Message) -> None:
        """
        Handles incoming state update messages.

        Args:
            body (dict): The message body.
            message (Message): The message instance.
        """
        routing_data = message.delivery_info.get('routing_key').split('.')
        [incoming_mark, device_type, device_uuid, packet_type] = routing_data

        if incoming_mark != self.incoming_mark:
            return message.requeue()

        if packet_type == SkabenPackets.SAVE.value:
            device_conf = get_device_config()
            device = device_conf.get_by_topic(device_type)
            if device.type == 'simple':
                message.ack()
                return

            serialized = device.schema(
                device.model.objects.get(uid=device_uuid),
                context=self.context,
                data=body,
                partial=True
            )
            if serialized.is_valid():
                serialized.save()
            else:
                return message.reject()

        message.ack()
