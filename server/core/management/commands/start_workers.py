from django.core.management.base import BaseCommand
from core.transport.queue_handlers import (
    BaseHandler,
    TranslatorHandler,
    InternalHandler,
    StateUpdateHandler,
    ClientUpdateHandler,
)
from core.transport.config import get_mq_config, SkabenQueue
from threading import Thread
from multiprocessing import Process

config = get_mq_config()


class Command(BaseCommand):
    """ Django command to start workers for RabbitMQ"""

    @staticmethod
    def bind_handler(handler: type(BaseHandler)) -> type(BaseHandler):
        # atm only to one
        return handler(
            config,
            config.queues.get(handler.incoming_mark)
        )

    def handle(self, *args, **options):
        for handler in [
            TranslatorHandler,
            InternalHandler,
            StateUpdateHandler,
            ClientUpdateHandler,
        ]:
            bound = self.bind_handler(handler)
            worker = Process(target=bound.run, name=f'{bound.incoming_mark}_thread')
            worker.start()
            self.stdout.write(self.style.SUCCESS(f'[+] worker started: {worker}'))

