import skabenproto
from kombu import Connection, Message, Exchange

from core.helpers import from_json, get_server_time


class QueueConsumer(object):
    """Базовый обработчик сообщений очереди"""

    outer_mqtt_mark = 'ask'
    datahold_packet_mark = ['cup', 'sup', 'info']

    def handle(self, body: str | dict, message: Message) -> dict:
        """Обрабатывает входящее сообщение"""
        routing_key = message.delivery_info.get('routing_key').split('.')
        # внутренние сообщения, не приходящие от клиентов из ask-exchange - уже обработаны
        if routing_key[0] != self.outer_mqtt_mark:
            return body

        try:
            routing_data = self.parse_routing_key(routing_key)
            payload_data = from_json(body)
        except Exception as e:
            raise Exception(f"cannot parse message payload `{body}` >> {e}")

        if routing_key[-1] in self.datahold_packet_mark:
            payload_data.update(self.parse_datahold(payload_data))

        return routing_data | payload_data  # merge two dictionaries

    @staticmethod
    def parse_routing_key(routing_key: str) -> dict:
        """Получение данных из routing key"""
        device_type, device_uid, command = routing_key
        data = dict(device_type=device_type,
                    device_uid=device_uid,
                    command=command)
        return data

    @staticmethod
    def parse_datahold(data: dict) -> dict:
        """Получение данных из воля datahold для умных устройств"""
        result = {'datahold': f'{data}'}
        if isinstance(data, dict):
            result = dict(
                timestamp=int(data.get('timestamp', 0)),
                task_id=data.get('task_id', 0),
                hash=data.get('hash', ''),
                datahold=from_json(data.get('datahold', {}))
            )
        return result

    def update_timestamp_only(self, parsed: dict, timestamp: str | int = ''):
        timestamp = timestamp or get_server_time()
        parsed.update(
            {
                'timestamp': timestamp,
                'datahold': {'timestamp': timestamp},
                'command': 'sup',
                'hash': parsed.get('hash', '')
            }
        )
        return parsed

    def __str__(self):
        return f"{self.__class__.__name__}"
