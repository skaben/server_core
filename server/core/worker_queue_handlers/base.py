import logging
from datetime import timedelta
from typing import Dict, List

from core.helpers import format_routing_key
from core.transport.config import MQConfig, get_connection
from core.transport.publish import publish
from django.conf import settings
from kombu import Message
from kombu.mixins import ConsumerProducerMixin
from core.redis_pool import get_redis_client

__all__ = ["BaseHandler"]


class BaseHandler(ConsumerProducerMixin):
    """
    Base class for message queue handlers.

    Attributes:
        running (bool): Indicates whether the handler is currently running.
        accepts (str): The message serialization format.
        outgoing_mark (str): The outgoing message mark.
        incoming_mark (str): The incoming message mark.
    """

    name: str = "base"
    running: bool
    accepts: str = "json"
    outgoing_mark: str
    incoming_mark: str | list

    def __init__(self, config: MQConfig, queues: Dict[str, str]):
        """
        Initializes the BaseHandler.

        Args:
            config (MQConfig): The message queue configuration.
            queues (dict): The queues for the handler.
        """
        self.config = config
        self.queues = queues
        self.redis_client = get_redis_client()
        self.connection = get_connection()

    def start(self):
        print(f"{self}: listening on {self.queues}")
        super().run(consumer_tag=self.name)

    def handle_message(self, body: Dict, message: Message) -> None:
        """
        Abstract method to be overridden by subclasses.

        Args:
            body (dict): The message body.
            message (Message): The message instance.
        """
        raise NotImplementedError

    def dispatch(self, data, routing_data: List[str], **kwargs) -> None:
        """
        Dispatches message.

        Args:
            data (dict): The message data.
            routing_data (list): The message routing data.
        """
        exchange = kwargs.get("exchange", self.config.internal_exchange)
        publish(body=data, exchange=exchange, routing_key=format_routing_key(*routing_data), **kwargs)

    def set_locked(self, key: str, timeout: int = 0):
        """
        Sets a lock for the given key using Redis.

        Args:
            key (str): The name of the lock key.
            timeout (int, optional): The timeout value for the lock, in seconds.
                If not specified, the value of `settings.DEVICE_KEEPALIVE_TIMEOUT` will be used.
        """
        timeout = timeout or settings.RESPONSE_TIMEOUT.get(self.incoming_mark, 10)
        self.redis_client.setex(key, timedelta(seconds=timeout), "lock")

    def get_locked(self, key: str) -> bool:
        """
        Checks whether a lock is set for the given key in Redis.

        Args:
            key (str): The name of the lock key.

        Returns:
            bool: True if a lock is set for the key, False otherwise.
        """
        return self.redis_client.get(key) is not None

    def get_consumers(self, consumer, channel) -> List:
        """
        Sets up the consumer and returns it as a list.

        Args:
            consumer: The consumer instance.
            channel: The message queue channel.

        Returns:
            list: The list of consumers.
        """
        consumer = consumer(
            queues=self.queues, accept=[self.accepts], callbacks=[self.handle_message], tag_prefix="skaben_"
        )
        logging.info(f"acquired broker connection with {consumer}")
        return [consumer]

    def __str__(self) -> str:
        """
        Returns a string representation of the BaseHandler.

        Returns:
            str: The string representation of the BaseHandler.
        """
        return self.__class__.__name__
