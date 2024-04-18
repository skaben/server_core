import asyncio
from functools import lru_cache
from typing import List
from django.conf import settings
from server.core.scheduler.tasks import (
    Task,
    AlertTask,
    PingerTask,
)


class SchedulerService:

    tasks: List[Task]
    running: asyncio.Event

    def __init__(self, tasks: List[Task]):
        """
        Initializes the SchedulerService.

        Args:
            tasks: List of tasks to be scheduled.
        """
        self.tasks = tasks
        self.running = asyncio.Event()

    async def start(self) -> None:
        """
        Starts the scheduler service.
        """
        self.running.set()
        await self.run()

    async def stop(self) -> None:
        """
        Stops the scheduler service.
        """
        self.running.clear()

    async def run_task(self, task: Task, timeout: int) -> None:
        """
        Runs a task asynchronously based on the specified timeout.

        Args:
            task: The task to run.
            timeout: The timeout value for the task.
        """
        while self.running.is_set():
            await task.run()
            await asyncio.sleep(timeout)

    async def run(self) -> None:
        """
        Runs the scheduler by executing all the tasks asynchronously.
        """
        coroutines = [self.run_task(task, task.timeout) for task in self.tasks]
        await asyncio.gather(*coroutines)


@lru_cache
def get_service() -> SchedulerService:
    """
    Retrieves the scheduler service with pre-configured tasks.

    Returns:
        The scheduler service object.
    """
    pinger = PingerTask(timeout=settings.RESPONSE_TIMEOUT.get("ping", 10))

    alert_timeout = int(settings.ALERT_COOLDOWN.get("increase", 60))

    increase_alert = AlertTask(timeout=alert_timeout)
    decrease_alert = AlertTask(timeout=alert_timeout)
    service = SchedulerService(
        tasks=[
            pinger,
            increase_alert,
            decrease_alert,
        ]
    )
    return service
