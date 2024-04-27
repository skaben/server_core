import logging
from typing import Dict, List

import settings
from alert.event_handling import handle as alert_handle
from core.helpers import get_server_timestamp
from core.transport.config import MQConfig, SkabenPackets, SkabenQueue
from core.worker_queue_handlers.base import BaseHandler
from django.db import models
from kombu import Message
from reactions import queue_events as reaction_events


class InternalHandler(BaseHandler):
    """
    Handler for incoming internal messages.

    Attributes:
        info_mark (str): The state mutate message mark.
        incoming_mark (str): The incoming message mark.
        keepalive_mark (str): The keepalive message mark.
        state_save_mark (str): The state save message mark.
        client_update_mark (str): The client update message mark.
    """

    name: str = "main_internal"
    info_mark: str = SkabenPackets.INFO.value
    incoming_mark: str = SkabenQueue.INTERNAL.value
    keepalive_mark: str = SkabenPackets.PONG.value
    state_save_mark: str = SkabenPackets.SAVE.value
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
        """Распознает внутренние сообщения в зависимости от заголовков.

        Args:
            body (dict): Тело сообщения.
            message (Message): Экземпляр сообщения.
        """
        try:
            if message.headers and message.headers.get("event_type"):
                # определяем, что сообщение является внутренним событием
                # пакеты не обладают заголовком event_type
                self.handle_event(message.headers, body)
            else:
                self.route_event(body, message)
        except Exception:  # noqa
            logging.exception(f"while handling internal queue message {message.headers} {message}")

    def route_event(self, body: Dict, message: Message) -> None:
        """Перенаправляет события в различные очереди, в зависимости от типа пакета.

        Args:
            body (dict): Тело сообщения.
            message (Message): Экземпляр сообщения.
        """
        routing_data: List[str] = message.delivery_info.get("routing_key").split(".")
        [incoming_mark, device_type, device_uuid, packet_type] = routing_data

        if incoming_mark != self.incoming_mark:
            return message.requeue()

        if packet_type == self.keepalive_mark:
            if message.headers.get("timestamp", 0) + settings.DEVICE_KEEPALIVE_TIMEOUT < get_server_timestamp():
                self.dispatch(body, [SkabenQueue.CLIENT_UPDATE.value, device_type, device_uuid])
        elif packet_type == self.state_save_mark:
            self.dispatch(body["datahold"], [SkabenQueue.STATE_UPDATE.value, device_type, device_uuid, packet_type])
        elif packet_type == self.client_update_mark:
            self.dispatch(
                body,
                [SkabenQueue.CLIENT_UPDATE.value, device_type, device_uuid],
                headers={"external": True},
            )
        elif packet_type == self.info_mark:
            body["datahold"].update(
                {
                    "device_type": device_type,
                    "device_uuid": device_uuid,
                }
            )
            self.handle_event("device", body["datahold"])
        else:
            return message.reject()

        if not message.acknowledged:
            message.ack()

    def handle_event(self, event_headers: dict, event_data: dict):
        """Обрабатывает события на основе типа события и данных.

        Это основная функция-обработчик, здесь применяются сценарии игры.

        Аргументы:
            headers (dict): Мета-данные события, включающие тип.
            event_data (dict): Полезная нагрузка события.
        """
        alert_handle(event_headers, event_data)
        # применение механики игры через пайплайн
        # reaction_events.handle(event_type, event_data)

    @staticmethod
    def get_instance(model: models.Model, uid: str):
        """
        Получает экземпляр модели.

        Args:
            model (type): The model type.
            uid (str): The model UID.

        Returns:
            The model instance.
        """
        return model.objects.get(uid=uid)
