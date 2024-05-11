import logging
from typing import Dict

from core.models import DeviceTopic
from core.transport.config import MQConfig, SkabenQueue
from core.transport.publish import get_interface
from core.transport.topics import get_topics
from core.worker_queue_handlers.base import BaseHandler
from kombu import Message
from peripheral_devices.service.packet_format import cup_packet_from_model
from peripheral_devices.service.passive_config import get_passive_config
from peripheral_devices.models.helpers import get_model_by_topic


class ClientUpdateHandler(BaseHandler):
    """
    Handler for incoming client update messages.

    Attributes:
        incoming_mark (str): The incoming message mark.
    """

    name: str = "client_updater"
    incoming_mark: str = SkabenQueue.CLIENT_UPDATE.value

    def __init__(self, config: MQConfig, queues: Dict[str, str]):
        """
        Initializes the ClientUpdateHandler.

        Args:
            config (MQConfig): The message queue configuration.
            queues (dict): The queues for the handler.
        """
        super().__init__(config, queues)
        self.all_topics = get_topics()

    def handle_message(self, body: Dict, message: Message) -> None:
        """Обрабатывает входящее сообщение."""
        routing_key = message.delivery_info.get("routing_key")
        routing_data = routing_key.split(".")
        incoming_mark = routing_data[0]
        device_topic = routing_data[1]
        device_uid = None

        if len(routing_data) > 2:
            device_uid = routing_data[2]

        if incoming_mark != self.incoming_mark:
            return message.requeue()

        if device_topic not in DeviceTopic.objects.get_topics_active():
            return message.ack()

        try:
            if device_topic not in DeviceTopic.objects.get_topics_permitted():
                logging.error(f"Client update wasn't handled. Unknown device `{device_topic}`")
                return message.reject()

            if device_topic in DeviceTopic.objects.get_topics_by_type("simple"):
                address = device_uid or "all"  # 'all' маркирует броадкастовую рассылку
                self.dispatch(routing_data=[device_topic, address], data=get_passive_config(device_topic))
                return message.ack()

            if device_topic in DeviceTopic.objects.get_topics_by_type("smart"):
                targets = []
                model = get_model_by_topic(device_topic)
                if device_uid == "all":
                    targets = list(model.objects.not_overridden())
                if device_uid and device_uid != "all":
                    targets = list(model.objects.filter(mac_address=device_uid))

                if targets:
                    with get_interface() as interface:
                        for target in targets:
                            packet = cup_packet_from_model(target)
                            if packet:
                                interface.send_mqtt(packet)

        except Exception:  # noqa
            logging.exception("Exception while handling client update.")
            return message.reject()

        if not message.acknowledged:
            return message.ack()

    @staticmethod
    def get_device_config(device_topic: str, device_uid: str, body: dict, message: Message):
        """Получает актуальную конфигурацию устройства."""
        model = get_model_by_topic(device_topic)
        try:
            instance = model.objects.get(mac_addr=device_uid)
            if instance.override:
                logging.warning(f"device {device_uid} is under override policy. skipping update")
                return
            update_packet = cup_packet_from_model(instance)
            if message.headers.get("force_update") or instance.get_hash() != body.get("hash", 1):
                return update_packet

        except model.DoesNotExist:
            # todo: operation of new device approval is not implemented yet
            logging.error(f"device of type {device_topic} with MAC {device_uid} not found in DB")
