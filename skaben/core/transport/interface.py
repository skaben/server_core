import logging
import traceback
import skabenproto

from core.transport.config import MQConfig, get_mq_config


class MQInterface(object):

    def __init__(self, config: MQConfig):
        self.config = config

    def send_mqtt_skaben(self, packet: skabenproto.BasePacket):
        """Отправить SKABEN пакет через MQTT"""
        return self.send_mqtt_raw(packet.topic, packet.payload)

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

    def send_internal(self, routing_key: str, payload: dict):
        return self._publish(
            payload,
            exchange=self.config.exchanges.get('internal'),
            routing_key=routing_key
        )

    def _publish(self, body: dict, exchange: str, routing_key: str):
        try:
            with self.config.pool.acquire() as channel:
                prod = self.config.conn.Producer(channel)
                prod.publish(
                    body,
                    exchange=exchange,
                    routing_key=routing_key,
                    retry=True
                )
        except Exception as e:
            logging.error(f'exception occured when sending packet to {routing_key}: {e}')

    def __str__(self):
        return f'<MQInterface ["config": {self.config}]>'

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return


def get_interface():
    return MQInterface(get_mq_config())