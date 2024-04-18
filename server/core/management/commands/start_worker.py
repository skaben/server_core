from django.core.management.base import BaseCommand
from core.transport.queue_handlers import (
    BaseHandler,
    AskHandler,
    InternalHandler,
    StateUpdateHandler,
    ClientUpdateHandler,
)
from core.transport.config import get_mq_config

config = get_mq_config()

HANDLERS = {
    "mqtt": AskHandler,
    "internal": InternalHandler,
    "state": StateUpdateHandler,
    "client": ClientUpdateHandler,
}

_handlers_help = f'[{"|".join(HANDLERS.keys())}]'


class Command(BaseCommand):
    """Django command to start workers for RabbitMQ"""

    help = f"python manage.py run_worker {_handlers_help}"

    def add_arguments(self, parser):
        parser.add_argument("handler", type=str, help=f"choose one from {_handlers_help}")

    @staticmethod
    def bind_handler(handler: type(BaseHandler)) -> type(BaseHandler):
        """Binds handler to queue.

        At this moment we can only bind one handler to one queue
        """
        return handler(config, config.queues.get(handler.incoming_mark))

    def handle(self, *args, **options):
        handler_type = options.get("handler", "")
        handler = HANDLERS.get(handler_type)
        if not handler_type or not handler:
            raise AttributeError(f"handler with name {handler_type} not configured")
        bound = self.bind_handler(handler)
        self.stdout.write(f"worker starting with handler {bound}")
        bound.start()
