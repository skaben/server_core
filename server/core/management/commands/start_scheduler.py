from django.core.management.base import BaseCommand
from server.core.scheduler.service import get_service
import asyncio
import time
from threading import Thread


class Command(BaseCommand):
    """Django command to start the scheduler for RabbitMQ"""

    help = 'Starts the scheduler for recurrent tasks.'

    async def run_scheduler(self) -> None:
        """
        Runs the scheduler asynchronously.
        """
        service = get_service()
        await service.start()
        self.stdout.write(self.style.SUCCESS('Scheduler running...'))

    def handle(self, *args: str, **options: str) -> None:
        """
        Handles the execution of the command.

        Args:
            *args: Positional arguments passed to the command.
            **options: Keyword arguments passed to the command.
        """
        loop = asyncio.get_event_loop()
        while True:
            try:
                self.stdout.write(self.style.SUCCESS('Starting scheduler...'))
                loop.run_until_complete(self.run_scheduler())
            except asyncio.CancelledError:
                self.stdout.write(self.style.WARNING('Scheduler stopped. Restarting...'))
                continue
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING('Scheduler stopped manually. Exiting...'))
                break
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Scheduler encountered an error: {e}'))
                break
            time.sleep(1)
