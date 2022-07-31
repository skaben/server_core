import kombu
import logging

from functools import lru_cache
from kombu import Connection, Exchange, Queue
from django.conf import settings

kombu.disable_insecure_serializers(allowed=['json'])


INTERNAL_QUEUES = [
            'log',
            'errors',
            'save'
        ]

DEVICE_QUEUES = [
            'cup',
            'sup',
            'info',
            'ack',
            'nack',
            'pong'
        ]


class MQFactory:

    @staticmethod
    def create_queue(queue_name: str, exchange: Exchange, is_topic: bool = True, **kwargs) -> Queue:
        routing_key = f'#.{queue_name}' if is_topic else queue_name
        return Queue(
            queue_name,
            durable=False,
            exchange=exchange,
            routing_key=routing_key,
            **kwargs
        )

    @staticmethod
    def create_exchange(channel, name: str, type: str = "topic"):
        exchange = Exchange(name, type=type)
        bound_exchange = exchange(channel)
        bound_exchange.declare()
        return bound_exchange


class MQConfig:

    exchanges: dict
    queues: dict

    def __init__(self):
        self.exchanges = {}
        self.queues = {}
        if not settings.AMQP_URI:
            logging.error('AMQP settings is missing, exchanges will not be initialized')
            return
        self.conn = Connection(settings.AMQP_URI)
        self.pool = self.conn.ChannelPool()

    def init_mqtt_exchange(self) -> dict:
        """Initialize MQTT exchange infrastructure"""
        logging.info('initializing mqtt exchange')
        with self.pool.acquire(timeout=settings.AMQP_TIMEOUT) as channel:
            # main mqtt exchange, used for messaging out.
            # note that all replies from clients starts with 'ask.' routing key goes to ask exchange
            self.exchanges.update(mqtt=MQFactory.create_exchange(channel, 'mqtt'))
        return self.exchanges

    def init_ask_exchange(self) -> dict:
        logging.info('initializing mqtt replies (ask) exchange')
        if not self.exchanges.get('mqtt'):
            self.init_mqtt_exchange()

        with self.pool.acquire(timeout=settings.AMQP_TIMEOUT) as channel:
            ask_exchange = MQFactory.create_exchange(channel, 'ask')
            ask_exchange.bind_to(exchange=self.exchanges['mqtt'],
                                 routing_key='ask.#',
                                 channel=channel)
            self.exchanges.update(ask=ask_exchange)
        return self.exchanges

    def init_internal_exchange(self):
        """Initializing internal direct exchange"""
        logging.info('initializing internal exchange')
        with self.pool.acquire(timeout=settings.AMQP_TIMEOUT) as channel:
            exchange = MQFactory.create_exchange(channel, 'internal', 'direct')
            self.exchanges.update(internal=exchange)
        return self.exchanges

    def init_transport_queues(self) -> dict:
        exchange = self.exchanges.get('ask')
        if not exchange:
            self.init_ask_exchange()

        q_names = DEVICE_QUEUES
        queues = {name: MQFactory.create_queue(name, exchange) for name in q_names}
        self.queues.update(**queues)
        return self.queues

    def init_internal_queues(self) -> dict:
        exchange = self.exchanges.get('internal')
        if not exchange:
            self.init_internal_exchange()

        q_names = INTERNAL_QUEUES
        queues = {name: MQFactory.create_queue(name, exchange, is_topic=False) for name in q_names}
        self.queues.update(**queues)
        return self.queues

    def __str__(self):
        return f"<MQConfig connected to {settings.AMQP_URI}>"


@lru_cache()
def get_mq_config():
    config = MQConfig()
    config.init_mqtt_exchange()
    if not settings.AMQP_LIMITED:
        config.init_transport_queues()
        config.init_internal_queues()
    return config
