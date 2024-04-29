import logging
from typing import Dict, List

import settings

from event_handling.alert_context import AlertEventContext as alert_context
from event_handling import device_context

from core.helpers import get_server_timestamp
from core.transport.config import MQConfig, SkabenQueue
from core.transport.packets import SkabenPacketTypes
from core.worker_queue_handlers.base import BaseHandler
from django.db import models
from kombu import Message

# TODO: разделить сущность на роутер и обработчика событий.
# в текущей реализации нарушается принцип single responsibility


class InternalHandler(BaseHandler):
    """Обработчик внутренней очереди."""

    name: str = "main_internal"

    incoming_mark: str = SkabenQueue.INTERNAL.value

    state_save_queue_mark: str = SkabenQueue.STATE_UPDATE.value
    client_update_queue_mark: str = SkabenQueue.CLIENT_UPDATE.value

    state_save_packet_mark: str = SkabenPacketTypes.SUP
    client_update_packet_mark: str = SkabenPacketTypes.CUP
    info_packet_mark: str = SkabenPacketTypes.INFO
    keepalive_packet_mark: str = SkabenPacketTypes.PONG

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
                # сообщение является событием внутренней очереди и должно быть обработано
                self.handle_event(message.headers, body)
            else:
                # пакеты не обладают заголовком event_type и отправляются в метод-роутер
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
        [incoming_mark, device_type, device_uid, packet_type] = routing_data

        if incoming_mark != self.incoming_mark:
            return message.requeue()

        logging.error(f"routing {incoming_mark} {device_type} {packet_type}")

        if packet_type == self.keepalive_packet_mark:
            if message.headers.get("timestamp", 0) + settings.DEVICE_KEEPALIVE_TIMEOUT < get_server_timestamp():
                self.dispatch(data=body, routing_data=[self.client_update_queue_mark, device_type, device_uid])
            return message.ack()

        if packet_type == self.state_save_packet_mark:
            self.dispatch(
                data=body["datahold"], routing_data=[self.state_save_queue_mark, device_type, device_uid, packet_type]
            )
            return message.ack()

        if packet_type == self.client_update_packet_mark:
            self.dispatch(
                data=body,
                routing_data=[self.client_update_queue_mark, device_type, device_uid],
            )
            return message.ack()

        # INFO-пакеты не переадресуются и обрабатываются здесь.
        if packet_type == self.info_packet_mark:
            # происходит конвертация INFO пакета в событие внутренней очереди.
            headers = {
                "event_type": "device",
                "event_source": "mqtt",
                "device_type": device_type,
                "device_uid": device_uid or None,
            }
            self.handle_event(headers, body["datahold"])
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
        with alert_context() as context:
            context.apply(event_headers, event_data)
        device_context.apply(event_headers, event_data)

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
