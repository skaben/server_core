from typing import Dict, List
from core.helpers import get_server_timestamp
from kombu import Message
from core.transport.config import SkabenQueue, SkabenPackets, MQConfig
from core.transport.queue_handlers import BaseHandler


class InternalHandler(BaseHandler):
    """
    Handler for incoming internal messages.

    Attributes:
        incoming_mark (str): The incoming message mark.
        keepalive_mark (str): The keepalive message mark.
        state_save_mark (str): The state save message mark.
        state_mutate_mark (str): The state mutate message mark.
        client_update_mark (str): The client update message mark.
    """
    name: str = 'main_internal'
    incoming_mark: str = SkabenQueue.NEW.value
    keepalive_mark: str = SkabenPackets.PONG.value
    state_save_mark: str = SkabenPackets.SAVE.value
    state_mutate_mark: str = SkabenPackets.INFO.value
    client_update_mark: str = SkabenPackets.CLIENT.value

    def __init__(self, config: MQConfig, queues: Dict[str, str]):
        """
        Initializes the InternalHandler.

        Args:
            config (MQConfig): The message queue configuration.
            queues (dict): The queues for the handler.
        """
        super().__init__(config, queues)

    def handle_message(self, body: Dict, message: Message) -> None:
        """
        Handles incoming internal messages.

        Args:
            body (dict): The message body.
            message (Message): The message instance.
        """
        routing_data: List[str] = message.delivery_info.get('routing_key').split('.')
        [incoming_mark, device_type, device_uuid, packet_type] = routing_data

        if incoming_mark != self.incoming_mark:
            return message.requeue()

        if packet_type == self.keepalive_mark:
            self.dispatch_keepalive(body, [device_type, device_uuid, packet_type])
        elif packet_type in (self.state_save_mark, self.state_mutate_mark):
            body['datahold'].update({"timestamp": body.get('timestamp', get_server_timestamp())})
            self.dispatch(
                body['datahold'],
                [SkabenQueue.STATE_UPDATE.value, device_type, device_uuid, packet_type]
            )
        elif packet_type == self.client_update_mark:
            self.dispatch(
                body,
                [SkabenQueue.CLIENT_UPDATE.value, device_type, device_uuid],
                headers={'external': True},
            )
        else:
            message.reject()
            return

        message.ack()

    def dispatch_keepalive(self, body: Dict, routing_data: List[str]) -> None:
        """
        Dispatches keepalive messages.

        Args:
            body (dict): The message body.
            routing_data (list): The message routing data.
        """
        if body.get('timestamp', 0) < get_server_timestamp():
            self.dispatch(
                body,
                [SkabenQueue.CLIENT_UPDATE.value, *routing_data]
            )
        else:
            self.dispatch(
                {'timestamp': body.get('timestamp')},
                [SkabenQueue.STATE_UPDATE.value, *routing_data]
            )

    @staticmethod
    def get_instance(model: type, uid: str):
        """
        Gets an instance of a model.

        Args:
            model (type): The model type.
            uid (str): The model UID.

        Returns:
            The model instance.
        """
        return model.objects.get(uid=uid)
