import logging
from kombu import Message
from kombu.mixins import ConsumerProducerMixin
from core.transport.config import MQConfig

__all__ = ['BaseHandler']


class BaseHandler(ConsumerProducerMixin):

    running: bool
    accepts: str = 'json'
    outgoing_mark: str
    incoming_mark: str

    def __init__(self, config: MQConfig, queues: dict):
        self.config = config
        self.queues = queues
        self.connection = config.conn

    def handle_message(self, body: dict, message: Message):
        raise NotImplementedError

    @staticmethod
    def get_routing_key(routing_data):
        return '.'.join(routing_data)

    def get_consumers(self, consumer, channel):
        """setup consumer and assign callback"""
        consumer = consumer(queues=self.queues,
                            accept=[self.accepts],
                            callbacks=[self.handle_message],
                            tag_prefix=f'skaben_')
        logging.info(f'acquired broker connection with {consumer}')
        return [consumer]

    def __str__(self):
        return f"{self.__class__.__name__} on {self.queues}"
