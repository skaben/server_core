import logging
from typing import Dict, List

import settings
from core.helpers import get_server_timestamp
from kombu import Message
from django.db import models
from core.transport.config import SkabenQueue, SkabenPackets, MQConfig
from core.devices import get_device_config
from core.transport.queue_handlers import BaseHandler
from reactions.main import apply_pipeline


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
                return self.handle_event(message.headers.get('event'), body)
            self.route_device_event(body, message)
        except Exception:  # noqa
            logging.exception('while handling internal queue message')

    def handle_event(self, event_type: str, event_data: dict):
        """
        Обрабатывает события на основе типа события и данных.

        Это основная функция-обработчик, здесь применяются сценарии игры.

        Аргументы:
            event_type (str): Тип события, связанного с событием.
            event_data (dict): Данные события.
        """
        devices = get_device_config()
        # базовая механика, применяющаяся вне зависимости от сценария игры
        if event_type == 'alert_state':
            # обновление конфигурации устройств при смене уровня тревоги
            for topic in devices.topics():
                if topic != 'scl':
                    self.dispatch({}, [SkabenQueue.CLIENT_UPDATE.value, topic])
        if event_type == 'alert_counter':
            # специальный посыл конфига для шкал
            self.dispatch({}, [SkabenQueue.CLIENT_UPDATE.value, 'scl'])
        # применение механики ЩИТКА (pwr)
        apply_pipeline(event_type, event_data)

    def route_device_event(self, body: Dict, message: Message):
        """
        Обрабатывает события, специфичные для устройства.

        Аргументы:
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
