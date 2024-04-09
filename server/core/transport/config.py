import kombu
import logging
from enum import Enum
from typing import List
from functools import lru_cache
from kombu import Connection, Exchange, Queue
from kombu.pools import connections
from django.conf import settings

kombu.disable_insecure_serializers(allowed=['json'])
ASK_QUEUE = 'ask'  # incoming mqtt filtering queue


def get_connection():
    return Connection(
        settings.AMQP_URI,
        transport_options={
            'confirm_publish': True,
        }
    )


def acquire_pool(func):
    def wrapper(self, *args, **kwargs):
        conn = get_connection()
        with connections[conn].acquire(block=True) as pool:
            return func(self, pool=pool, *args, **kwargs)
    return wrapper


class SkabenPackets(Enum):
    ASK = 'ask'
    CLIENT = 'cup'
    SAVE = 'sup'
    INFO = 'info'
    PING = 'ping'
    PONG = 'pong'


class SkabenQueue(Enum):

    INTERNAL = 'internal'
    STATE_UPDATE = 'state_update'
    CLIENT_UPDATE = 'client_update'
    EVENT = 'event'


class MQFactory:

    @staticmethod
    def create_queue(queue_name: str, exchange: Exchange, is_topic: bool = True, **kwargs) -> Queue:
        routing_key = queue_name if not is_topic else f'{queue_name}.#'
        return Queue(
            queue_name,
            exchange=exchange,
            routing_key=routing_key,
            **kwargs
        )

    @staticmethod
    def create_exchange(channel, name: str, routing_type: str):
        exchange = Exchange(name, routing_type)
        bound_exchange = exchange(channel)
        # bound_exchange.declare()
        return bound_exchange


class MQConfig:

    exchanges: dict
    queues: dict

    def __init__(self):
        if not settings.AMQP_URI:
            raise AttributeError('CRIT: settings.AMQP_URI is missing, exchanges will not be initialized')

        self.queues = {}
        self.exchanges = {}
        self._init_mqtt_exchange()
        filtering_queue = {
            ASK_QUEUE: MQFactory.create_queue(
                ASK_QUEUE,
                self.mqtt_exchange,
                durable=True,
            )
        }
        transport_queues = {
            e.value: MQFactory.create_queue(
                e.value,
                self.internal_exchange,
                durable=False
            )
            for e in SkabenQueue
        }
        queues_full = transport_queues | filtering_queue
        self.bind_queues(queues=queues_full)
        self.queues = queues_full

    @property
    def internal_exchange(self) -> Exchange:
        return self.exchanges.get('internal', self._init_internal_exchange())

    @property
    def mqtt_exchange(self) -> Exchange:
        return self.exchanges.get('mqtt', self._init_mqtt_exchange())

    @acquire_pool
    def bind_queues(self, queues, pool):
        for queue in queues.values():
            bound_queue = queue(pool)
            bound_queue.declare()

    @acquire_pool
    def _init_mqtt_exchange(self, pool) -> Exchange:
        """Initialize MQTT exchange infrastructure"""
        logging.info('initializing mqtt exchange')
        # main mqtt exchange, used for messaging out.
        # note that all replies from clients starts with 'ask.'
        # routing key goes to internal exchange
        exchange = MQFactory.create_exchange(pool, 'mqtt', 'topic')
        self.exchanges.update(mqtt=exchange)
        return exchange

    @acquire_pool
    def _init_internal_exchange(self, pool) -> Exchange:
        """Initializing internal exchange"""
        logging.info('initializing internal exchange')
        exchange = MQFactory.create_exchange(pool, 'internal', 'topic')
        self.exchanges.update(internal=exchange)
        return exchange

    def __str__(self):
        return f"<MQConfig exchanges: " \
               f"{','.join(list(self.exchanges.keys()))} | " \
               f"queues: {','.join(list(self.queues.keys()))}>"


@lru_cache()
def get_mq_config() -> MQConfig:
    return MQConfig()
