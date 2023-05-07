from typing import Dict, Union
from kombu import Message

from core.helpers import from_json
from core.transport.config import SkabenQueue, SkabenPackets, MQConfig
from core.transport.queue_handlers import BaseHandler


class AskHandler(BaseHandler):
    """Incoming messages from MQTT terminates here.
        Providing translation into internal format and passing results to internal queue.
    """
    name: str = 'mqtt_bridge_ask_handler'
    incoming_mark: str = SkabenPackets.ASK.value
    outgoing_mark: str = SkabenQueue.NEW.value
    datahold_packet_mark: list[str] = [
        SkabenPackets.INFO.value,
        SkabenPackets.CLIENT.value,
        SkabenPackets.SAVE.value,
    ]

    def __init__(self, config: MQConfig, queues: Dict[str, str]):
        """
        Initializes the TranslatorHandler.

        Args:
            config (MQConfig): The message queue configuration.
            queues (dict): The queues for the handler.
        """
        super().__init__(config, queues)

    def handle_message(self, body: Union[str, Dict], message: Message) -> None:
        """
        Handles incoming messages.

        Args:
            body (Union[str, Dict]): The message body.
            message (Message): The message instance.
        """
        routing_key = message.delivery_info.get('routing_key')
        [routing_type, device_type, device_uuid, packet_type] = routing_key.split('.')

        if routing_type != self.incoming_mark:
            message.requeue()
            return

        # if the same key has already handled in time interval (default = 10) - ack and do nothing
        if self.get_locked(routing_key):
            message.ack()
            return
        self.set_locked(routing_key)

        try:
            payload_data = from_json(body)
            if packet_type in self.datahold_packet_mark:
                payload_data.update(self.parse_datahold(payload_data))
        except Exception as e:
            message.reject()
            raise Exception(f"cannot parse message payload `{body}` >> {e}")
        message.ack()
        self.dispatch(
            payload_data,
            [self.outgoing_mark, device_type, device_uuid, packet_type]
        )

    @staticmethod
    def parse_datahold(data: Union[str, Dict]) -> Dict:
        """
        Parses datahold from a message.

        Args:
            data (Union[str, Dict]): The message data.

        Returns:
            The parsed datahold.
        """
        result = {'datahold': f'{data}'}
        if isinstance(data, dict):
            result = dict(
                timestamp=int(data.get('timestamp', 0)),
                task_id=data.get('task_id', 0),
                hash=data.get('hash', ''),
                datahold=from_json(data.get('datahold', {}))
            )
        return result
