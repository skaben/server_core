import kombu
import logging
from enum import Enum
from typing import List
from functools import lru_cache
from kombu import Connection, Exchange, Queue
from django.conf import settings

kombu.disable_insecure_serializers(allowed=["json"])
ASK_QUEUE = "ask"  # incoming mqtt filtering queue


class SkabenPackets(Enum):
    ASK = "ask"
    CLIENT = "cup"
    SAVE = "sup"
    INFO = "info"
    PING = "ping"
    PONG = "pong"


class SkabenQueue(Enum):

    INTERNAL = "internal"
    STATE_UPDATE = "state_update"
    CLIENT_UPDATE = "client_update"
    EVENT = "event"


class MQFactory:

    @staticmethod
    def create_queue(queue_name: str, exchange: Exchange, is_topic: bool = True, **kwargs) -> Queue:
        routing_key = queue_name if not is_topic else f"{queue_name}.#"
        return Queue(queue_name, exchange=exchange, routing_key=routing_key, **kwargs)

    @staticmethod
    def create_exchange(channel, name: str, routing_type: str):
        exchange = Exchange(name, routing_type)
        bound_exchange = exchange(channel)
        bound_exchange.declare()
        return bound_exchange


class MQConfig:

    exchanges: dict
    queues: dict

    def __init__(self):
        if not settings.AMQP_URI:
            raise AttributeError("CRIT: settings.AMQP_URI is missing, exchanges will not be initialized")

        self.queues = {}
        self.exchanges = {}
        self.conn = Connection(settings.AMQP_URI)
        self.pool = self.conn.ChannelPool()
        self._init_mqtt_exchange()
        filtering_queue = {ASK_QUEUE: MQFactory.create_queue(ASK_QUEUE, self.mqtt_exchange, durable=True)}
        transport_queues = {
            e.value: MQFactory.create_queue(e.value, self.internal_exchange, durable=False) for e in SkabenQueue  # noqa
        }
        queues_full = transport_queues | filtering_queue
        self.bind_queues(queues_full)
        self.queues = queues_full

    @property
    def internal_exchange(self) -> Exchange:
        return self.exchanges.get("internal", self._init_internal_exchange())

    @property
    def mqtt_exchange(self) -> Exchange:
        return self.exchanges.get("mqtt", self._init_mqtt_exchange())

    def bind_queues(self, queues):
        with self.pool.acquire(timeout=settings.AMQP_TIMEOUT) as channel:
            for queue in queues.values():
                bound_queue = queue(channel)
                bound_queue.declare()

    def _init_mqtt_exchange(self) -> Exchange:
        """Initialize MQTT exchange infrastructure"""
        logging.info("initializing mqtt exchange")
        with self.pool.acquire(timeout=settings.AMQP_TIMEOUT) as channel:
            # main mqtt exchange, used for messaging out.
            # note that all replies from clients starts with 'ask.' routing key goes to internal exchange
            exchange = MQFactory.create_exchange(channel, "mqtt", "topic")
            self.exchanges.update(mqtt=exchange)
            return exchange

    def _init_internal_exchange(self) -> Exchange:
        """Initializing internal exchange"""
        logging.info("initializing internal exchange")
        with self.pool.acquire(timeout=settings.AMQP_TIMEOUT) as channel:
            exchange = MQFactory.create_exchange(channel, "internal", "topic")
            self.exchanges.update(internal=exchange)
            return exchange

    def __str__(self):
        return (
            f"<MQConfig exchanges: "
            f"{','.join(list(self.exchanges.keys()))} | "
            f"queues: {','.join(list(self.queues.keys()))}>"
        )


@lru_cache()
def get_mq_config() -> MQConfig:
    return MQConfig()
