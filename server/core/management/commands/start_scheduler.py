import asyncio
import time

from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand
from server.core.scheduler.service import get_service


class Command(BaseCommand):
    """Django command to start the scheduler for RabbitMQ"""

    help = "Starts the scheduler for recurrent tasks."

    async def run_scheduler(self) -> None:
        """
        Runs the scheduler asynchronously.
        """
        self.stdout.write(self.style.SUCCESS("Scheduler starting..."))
        _get_service = sync_to_async(get_service)
        service = await _get_service()
        await service.start()

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
                loop.run_until_complete(self.run_scheduler())
            except asyncio.CancelledError:
                self.stdout.write(self.style.WARNING("Scheduler stopped. Restarting..."))
                continue
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING("Scheduler stopped manually. Exiting..."))
                break
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Scheduler encountered an error: {e}"))
                break
            time.sleep(1)
