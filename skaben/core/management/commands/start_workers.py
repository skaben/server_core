from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """ Django command to start workers for RabbitMQ"""

    def handle(self, *args, **options):
        print('not implemented')
        # run_workers()
        # self.stdout.write(self.style.SUCCESS('workers started!'))
        # run_pinger()
        # self.stdout.write(self.style.SUCCESS('pingers started!'))
