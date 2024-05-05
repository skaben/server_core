import asyncio

from typing import List

from django.conf import settings
from server.core.scheduler.tasks import AlertTask, PingerTask, SkabenTask


class SchedulerService:
    """Сервис планировщика задач."""

    running: asyncio.Event
    task_queue: asyncio.Queue
    tasks_initial: List[SkabenTask]

    def __init__(self, task_queue: asyncio.Queue, tasks: List[SkabenTask]):
        self.tasks_initial = tasks
        self.task_queue = task_queue
        self.running = asyncio.Event()

    async def start(self) -> None:
        self.running.set()
        await self.run()

    async def stop(self) -> None:
        self.running.clear()

    async def run_task(self, task: SkabenTask) -> None:
        while self.running.is_set():
            await task.run()

    async def run(self) -> None:
        for task in self.tasks_initial:
            await self.task_queue.put(task)

        while self.running.is_set():
            try:
                next_task = await self.task_queue.get()
                await self.run_task(next_task)
            except asyncio.CancelledError:
                raise


def get_service() -> SchedulerService:
    """Создает экземпляр планировщика для регулярных задач."""
    # todo: replace asyncio.queue with Redis | Rabbit
    queue = asyncio.Queue()
    pinger = PingerTask(timeout=settings.RESPONSE_TIMEOUT.get("ping", 10), task_queue=queue, requeue=True)
    alert_task = AlertTask(timeout=settings.SCHEDULER_TASK_TIMEOUT, task_queue=queue, requeue=True)
    service = SchedulerService(tasks=[alert_task, pinger], task_queue=queue)
    return service
