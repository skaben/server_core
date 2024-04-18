import logging
from typing import Dict, List
from collections import namedtuple
from kombu import Message
from core.transport.queue_handlers import BaseHandler
from core.transport.publish import get_interface
from core.transport.config import SkabenQueue, MQConfig
from core.devices import get_device_config
from skabenproto import CUP
from core.helpers import get_server_timestamp

from peripheral_behavior.helpers import get_passive_config


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
        self.devices = get_device_config()
        self.ext_publisher = get_interface()

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
        device_type = routing_data[1]
        device_uid = None

        if len(routing_data) > 2:
            device_uid = routing_data[2]

        if incoming_mark != self.incoming_mark:
            return message.requeue()

        # device has already been updated
        if message.headers.get("external") and self.get_locked(routing_key):
            return message.reject()

        try:
            if device_type in self.devices.topics("simple"):
                current_config = get_passive_config(device_type)
                address = device_uid or "all"  # 'all' маркирует броадкастовую рассылку
                self.dispatch(current_config, [device_type, address])
                return message.ack()

            device = self.devices.get_by_topic(device_type)
            if device_uid:
                self.send_config(device, device_uid, body, message)
            else:
                list_of_devices = device.model.objects.exclude(override=True).values_list("mac_addr", flat=True)
                mac_addr_list = list(list_of_devices)
                for mac in mac_addr_list:
                    self.send_config(device, mac, body, message)

        except Exception:  # noqa
            return message.reject()
        message.ack()

    def send_config(self, device: namedtuple, device_uid: str, body: dict, message: Message):
        try:
            instance_data = self.get_instance_data(device, device_uid)
            if instance_data.get("override"):
                logging.warning(f"device {device_uid} is under override policy. skipping update")
                return

            if message.headers.get("force_update") or instance_data.get("hash", 0) != body.get("hash", 1):
                self.dispatch(
                    instance_data,
                    [device.topic, device_uid],
                )
        except device.model.DoesNotExist:
            # todo: operation of new device approval is not implemented yet
            logging.error(f"device of type {device.topic} with MAC {device_uid} not found in DB")
            raise

    def dispatch(self, data: Dict, routing_data: List[str], **kwargs) -> None:
        """Dispatches message to external MQTT."""
        if data:
            [device_type, device_uid] = routing_data
            packet = CUP(
                topic=device_type, uid=device_uid, task_id="n/a", datahold=data, timestamp=get_server_timestamp()
            )
            self.ext_publisher.send_mqtt_skaben(packet)

    @staticmethod
    def get_instance_data(device: namedtuple, mac_id: str) -> Dict:
        """
        Returns instance data as a dictionary.

        Args:
            device: The device.
            mac_id: The device's MAC ID.

        Returns:
            dict: The instance data as a dictionary.
        """
        instance = device.model.objects.get(mac_addr=mac_id)
        serializer = device.serializer(instance=instance)
        return serializer.data
