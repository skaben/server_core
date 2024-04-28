from typing import Dict

from kombu import Message

from core.models.mqtt import DeviceTopic
from core.transport.config import MQConfig, SkabenQueue
from core.transport.packets import SkabenPacketTypes
from core.worker_queue_handlers.base import BaseHandler
from peripheral_devices.models.helpers import get_model_by_topic, get_serializer_by_topic


class StateUpdateHandler(BaseHandler):
    """
    Handler for state update messages.
    """

    name: str = "state_update"
    context: Dict[str, bool] = {"no_send": True}
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
        routing_data = message.delivery_info.get("routing_key").split(".")
        [incoming_mark, device_topic, device_uid, packet_type] = routing_data

        if incoming_mark != self.incoming_mark:
            return message.requeue()

        if packet_type == SkabenPacketTypes.SUP:
            if device_topic in DeviceTopic.objects.get_topics_by_type("smart"):
                model = get_model_by_topic(device_topic)
                serializer = get_serializer_by_topic(device_topic)

                serialized = serializer(
                    model.objects.get(uid=device_uid), context=self.context, data=body, partial=True
                )
                if serialized.is_valid():
                    serialized.save()
                else:
                    return message.reject()

        if not message.acknowledged:
            message.ack()
