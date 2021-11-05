import time

from django.core.management.base import BaseCommand
from transport.tasks.main import run_pinger, run_workers


class Command(BaseCommand):
    """ Django command to start workers for RabbitMQ"""

    def handle(self, *args, **options):
        run_workers()
        self.stdout.write(self.style.SUCCESS('workers started!'))
        run_pinger()
        self.stdout.write(self.style.SUCCESS('pingers started!'))
