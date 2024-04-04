import logging
from typing import Dict, List

import settings

from core.helpers import get_server_timestamp
from kombu import Message
from django.db import models
from core.transport.config import SkabenQueue, SkabenPackets, MQConfig
from core.transport.queue_handlers import BaseHandler

from alert import event_handlers as alert_handlers
from reactions import event_handlers as reaction_handlers


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
    name: str = 'main_internal'
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
        """
        Routes incoming internal messages.

        Args:
            body (dict): The message body.
            message (Message): The message instance.
        """
        try:
            if message.headers and message.headers.get('event'):
                # сообщение уже было обработано ранее
                self.handle_event(message.headers.get('event'), body)
            else:
                self.route_event(body, message)
        except Exception:  # noqa
            logging.exception('while handling internal queue message')

    def route_event(self, body: Dict, message: Message) -> None:
        """Перенаправляет события в различные очереди, в зависимости от типа пакета.

        Args:
            body (dict): Тело сообщения.
            message (Message): Экземпляр сообщения.
        """
        routing_data: List[str] = message.delivery_info.get('routing_key').split('.')
        [incoming_mark, device_type, device_uuid, packet_type] = routing_data

        if incoming_mark != self.incoming_mark:
            return message.requeue()

        if packet_type == self.keepalive_mark:
            if message.headers.get('timestamp', 0) + settings.DEVICE_KEEPALIVE_TIMEOUT < get_server_timestamp():
                self.dispatch(
                    body,
                    [SkabenQueue.CLIENT_UPDATE.value, device_type, device_uuid]
                )
        elif packet_type == self.state_save_mark:
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
        elif packet_type == self.info_mark:
            logging.info(f'{message} {body}')
            body['datahold'].update({
                'device_type': device_type,
                'device_uuid': device_uuid,
            })
            self.handle_event('device', body['datahold'])
        else:
            return message.reject()

        if not message.acknowledged:
            message.ack()
    
    def handle_event(self, event_type: str, event_data: dict):
        """Обрабатывает события на основе типа события и данных.

        Это основная функция-обработчик, здесь применяются сценарии игры.

        Аргументы:
            event_type (str): Тип события, связанного с событием.
            event_data (dict): Данные события.
        """
        alert_handlers.handle(event_type, event_data)
        # применение механики игры через пайплайн
        reaction_handlers.handle(event_type, event_data)

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
