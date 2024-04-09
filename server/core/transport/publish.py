import logging
import traceback
import skabenproto

from kombu import Connection
from kombu.pools import producers

from django.conf import settings

from core.transport.config import (
    MQConfig,
    get_connection,
    get_mq_config,
    SkabenQueue
)


class MQPublisher(object):
    """Паблишер для очередей. Предназначен для использования другими модулями."""

    def __init__(self, config: MQConfig):
        self.config = config

    def send_mqtt_skaben(self, packet: skabenproto.BasePacket):
        """Отправить SKABEN пакет через MQTT"""
        topic = '.'.join(packet.topic.split('/'))
        return self.send_mqtt_raw(topic, packet.payload)

    def send_mqtt_raw(self, topic: str, message: str | dict):
        """Отправить команду в MQTT"""
        try:
            kwargs = {
                "body": message,
                "exchange": self.config.exchanges.get('mqtt'),
                "routing_key": f"{topic}"
            }
            return self._publish(**kwargs)
        except Exception:
            raise Exception(f"{traceback.format_exc()}")

    def send_event(self, event_type: str, payload: dict):
        """Отправляет событие с заголовками."""
        payload = payload or {}

        return self.send_internal(
            payload=payload,
            headers={'event': event_type},
            routing_key=f'{SkabenQueue.INTERNAL.value}',
        )

    def send_internal(self, routing_key: str, payload: dict, **kwargs):
        """Отправляет сообщение во внутреннюю очередь."""
        payload = payload or {}

        return self._publish(
            body=payload,
            exchange=self.config.exchanges.get('internal'),
            routing_key=routing_key,
            **kwargs,
        )

    def _publish(self, body: dict, exchange: str, routing_key: str, **kwargs):
        body = body or {}
        conn = get_connection()

        try:
            with producers[conn].acquire(block=True) as prod:
                prod.publish(
                    body,
                    exchange=exchange,
                    declare=[exchange],
                    routing_key=routing_key,
                    retry=True,
                    **kwargs,
                )
        except Exception as e:
            logging.error(f'[sync] exception occurred when sending packet to {routing_key}: {e}')

    def __str__(self):
        return f'<MQPublisher ["config": {self.config}]>'

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return


def get_interface():
    return MQPublisher(get_mq_config())
