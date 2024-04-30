import logging
from typing import Dict, List

from core.helpers import get_server_timestamp
from core.models import DeviceTopic
from core.transport.config import MQConfig, SkabenQueue
from core.transport.packets import CUP
from core.transport.publish import get_interface
from core.transport.topics import get_topics
from core.worker_queue_handlers.base import BaseHandler
from kombu import Message
from peripheral_behavior.helpers import get_passive_config
from peripheral_devices.models import SkabenDevice
from peripheral_devices.models.helpers import get_model_by_topic, get_serializer_by_topic
from rest_framework.serializers import ModelSerializer


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
        """
        Handles incoming client update messages.

        Args:
            body (dict): The message body.
            message (Message): The message instance.
        """
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
                logging.error(f"Client update not handled. Uknown device with device type `{device_topic}`")
                return message.reject()

            if device_topic in DeviceTopic.objects.get_topics_by_type("simple"):
                address = device_uid or "all"  # 'all' маркирует броадкастовую рассылку
                self.dispatch(
                    routing_data=[device_topic, address],
                    data=get_passive_config(device_topic),
                )
                return message.ack()

            if device_topic in DeviceTopic.objects.get_topics_by_type("smart"):
                if device_uid and device_uid != "all":
                    config = self.get_device_config(device_topic, device_uid, body, message)
                    self.dispatch(
                        routing_data=[device_topic, device_uid],
                        data=config,
                    )

                if device_uid == "all":
                    model = get_model_by_topic(device_topic)
                    serializer = get_serializer_by_topic(device_topic)
                    list_of_devices = model.objects.exclude(override=True)
                    for device in list_of_devices:
                        serialized = serializer(device)
                        if not serialized.is_valid():
                            logging.error(f"Validation error: cannot send config for {device}")
                        self.send_config(
                            routing_data=[device_topic, device.mac_addr],
                            data=serialized.data,
                        )
        except Exception:  # noqa
            logging.exception("Exception while handling client update.")
            return message.reject()

        if not message.acknowledged:
            return message.ack()

    def get_device_config(self, device_topic, device_uid: str, body: dict, message: Message):
        model = get_model_by_topic(device_topic)
        serializer = get_serializer_by_topic(device_topic)
        try:
            instance_data = self.get_instance_data(model, serializer, device_uid)
            if instance_data.get("override"):
                logging.warning(f"device {device_uid} is under override policy. skipping update")
                return

            if message.headers.get("force_update") or instance_data.get("hash", 0) != body.get("hash", 1):
                return instance_data
        except model.DoesNotExist:
            # todo: operation of new device approval is not implemented yet
            logging.error(f"device of type {device_topic} with MAC {device_uid} not found in DB")

    def dispatch(self, data, routing_data: List[str], **kwargs) -> None:
        """Dispatches message to external MQTT."""
        if data:
            packet = CUP(
                topic=routing_data[0],
                uid=routing_data[1],
                datahold=data,
                timestamp=get_server_timestamp(),
            )
            if routing_data[0] in DeviceTopic.objects.get_topics_by_type("smart") and data.get("hash"):
                packet.config_hash = data["hash"]

            with get_interface() as publisher:
                publisher.send_mqtt(packet)

    @staticmethod
    def get_instance_data(model: SkabenDevice, serializer: ModelSerializer, mac_id: str) -> Dict:
        """
        Returns instance data as a dictionary.

        Args:
            device: The device.
            mac_id: The device's MAC ID.

        Returns:
            dict: The instance data as a dictionary.
        """
        instance = model.objects.get(mac_addr=mac_id)
        serializer = serializer(instance=instance)
        return serializer.data
