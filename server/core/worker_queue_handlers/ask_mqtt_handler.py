"""Описывает работу обработчика для ask exchange - входящих MQTT пакетов."""

from typing import Dict, Union

from core.helpers import from_json, get_server_timestamp
from core.models.base import DeviceKeepalive
from core.models.mqtt import DeviceTopic
from core.transport.config import MQConfig, SkabenQueue
from core.transport.packets import SkabenPacketTypes
from core.worker_queue_handlers.base import BaseHandler
from kombu import Message

# TODO: применить здесь систему SkabenEvent


class AskHandler(BaseHandler):
    """Конвертирует входящие сообщения из MQTT в сообщения внутренней очереди."""

    name: str = "mqtt_bridge_ask_handler"
    incoming_mark: str = SkabenQueue.ASK.value
    outgoing_mark: str = SkabenQueue.INTERNAL.value
    datahold_packet_mark: list[str] = [SkabenPacketTypes.INFO, SkabenPacketTypes.CUP, SkabenPacketTypes.SUP]

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
        [routing_type, device_type, device_uid, packet_type] = routing_key.split(".")

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
                send_config = False
                payload_data.update(self.parse_datahold(payload_data))
                # сейчас адресация по маку поддерживается только для SMART устройств
                if device_type in DeviceTopic.objects.get_topics_smart():
                    timestamp, send_config = self.keepalive_status(device_uid, get_server_timestamp())
                if send_config:
                    # Любой пакет от устройства с просроченным timestamp будет отброшен
                    # Вместо ответа на пакет сервер посылает текущий конфиг устройства
                    self.dispatch(
                        data={},
                        routing_data=[self.outgoing_mark, device_type, device_uid, SkabenPacketTypes.CUP],
                        headers={"timestamp": timestamp},
                    )
                    return message.ack()
        except Exception as e:
            message.reject()
            raise Exception(f"cannot parse message payload `{body}` >> {e}")

        message.ack()
        self.dispatch(
            data=payload_data,
            routing_data=[self.outgoing_mark, device_type, device_uid, packet_type],
            headers={"timestamp": timestamp},
        )

    @staticmethod
    def keepalive_status(mac_addr: str, timestamp: int) -> [int, bool]:
        try:
            keepalive = DeviceKeepalive.objects.get(mac_addr=mac_addr)
            result = timestamp, keepalive.online
            keepalive.timestamp = timestamp
            keepalive.save()
        except DeviceKeepalive.DoesNotExist:
            timestamp = get_server_timestamp()
            DeviceKeepalive.objects.create(timestamp=timestamp, mac_addr=mac_addr)
            result = timestamp, True
        return result

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
