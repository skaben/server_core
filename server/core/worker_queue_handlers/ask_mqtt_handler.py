"""Описывает работу обработчика для ask exchange - входящих MQTT пакетов."""

from typing import Dict, Union

from core.helpers import from_json, get_server_timestamp
from core.models.base import DeviceKeepalive
from core.transport.config import MQConfig, SkabenPackets, SkabenQueue
from core.worker_queue_handlers.base import BaseHandler
from kombu import Message


class AskHandler(BaseHandler):
    """Incoming messages from MQTT terminates here.
    Providing translation into internal format and passing results to internal queue.
    """

    name: str = "mqtt_bridge_ask_handler"
    incoming_mark: str = SkabenPackets.ASK.value
    outgoing_mark: str = SkabenQueue.INTERNAL.value
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
        routing_key = message.delivery_info.get("routing_key")
        [routing_type, device_type, device_uuid, packet_type] = routing_key.split(".")

        if routing_type != self.incoming_mark:
            message.requeue()
            return

        # todo: improve de-dup
        # if the same key has already handled in time interval (default = 10) - ack and do nothing
        # if self.get_locked(routing_key):
        #     message.ack()
        #     return
        # self.set_locked(routing_key)

        timestamp = 0
        try:
            payload_data = from_json(body)
            if packet_type in self.datahold_packet_mark:
                payload_data.update(self.parse_datahold(payload_data))
            try:
                timestamp = self.save_timestamp(device_uuid, get_server_timestamp())
            except DeviceKeepalive.DoesNotExist:
                self.dispatch(
                    {"message": "new device active"},
                    [self.outgoing_mark, device_type, device_uuid, SkabenPackets.INFO.value],
                )
        except Exception as e:
            message.reject()
            raise Exception(f"cannot parse message payload `{body}` >> {e}")

        message.ack()
        self.dispatch(
            payload_data,
            [self.outgoing_mark, device_type, device_uuid, packet_type],
            headers={"timestamp": timestamp},
        )

    @staticmethod
    def save_timestamp(mac_addr: str, timestamp: int) -> int:
        try:
            obj = DeviceKeepalive.objects.get(mac_addr=mac_addr)
            obj.previous = obj.timestamp
            obj.timestamp = timestamp
            obj.save()
            return obj.previous
        except DeviceKeepalive.DoesNotExist:
            DeviceKeepalive.objects.create(previous=timestamp, timestamp=timestamp, mac_addr=mac_addr)

    @staticmethod
    def parse_datahold(data: Union[str, Dict]) -> Dict:
        """
        Parses datahold from a message.

        Args:
            data (Union[str, Dict]): The message data.

        Returns:
            The parsed datahold.
        """
        result = {"datahold": f"{data}"}
        if isinstance(data, dict):
            result = dict(
                timestamp=int(data.get("timestamp", 0)),
                task_id=data.get("task_id", 0),
                hash=data.get("hash", ""),
                datahold=from_json(data.get("datahold", {})),
            )
        return result
