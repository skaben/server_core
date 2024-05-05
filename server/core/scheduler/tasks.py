import asyncio
from django.conf import settings
from asgiref.sync import sync_to_async
from core.models.mqtt import DeviceTopic
from core.transport.packets import PING
from core.transport.publish import get_interface
from event_contexts.alert.utils import create_alert_auto_event


class SkabenTask:
    """Абстрактный класс задач для Планировщика."""

    timeout: int
    requeue: bool
    task_queue: asyncio.Queue

    def __init__(self, timeout: int, task_queue: asyncio.Queue, requeue: bool = False):
        self.timeout = timeout
        self.task_queue = task_queue
        self.requeue = requeue

    async def run(self) -> None:
        raise NotImplementedError("Subclasses must implement the run() method.")


class PingerTask(SkabenTask):
    """Отправляет пакеты PING в каждый активный MQTT топик."""

    def __init__(self, timeout: int, task_queue: asyncio.Queue, requeue: bool = False):
        super().__init__(timeout, task_queue, requeue)

    def _run(self) -> None:
        with get_interface() as publisher:
            for topic in DeviceTopic.objects.get_topics_active():
                packet = PING(topic=topic)
                publisher.send_mqtt(packet)

    async def run(self) -> None:
        await sync_to_async(self._run)()
        await asyncio.sleep(self.timeout)
        if self.requeue:
            await self.task_queue.put(PingerTask(self.timeout, self.task_queue, requeue=True))


class AlertTask(SkabenTask):
    """Отслеживает состояние уровня тревоги и изменяет счетчик тревоги."""

    def __init__(self, timeout: int, task_queue: asyncio.Queue, requeue: bool = False):
        super().__init__(timeout, task_queue, requeue)

    def _run(self) -> int:
        try:
            auto_event = create_alert_auto_event()
            if auto_event:
                event, timeout = auto_event
                with get_interface() as publisher:
                    publisher.send_event(event)
                self.timeout = timeout
            else:
                self.timeout = settings.SCHEDULER_TASK_TIMEOUT
        except Exception:  # noqa
            self.timeout = settings.SCHEDULER_TASK_TIMEOUT
        return self.timeout

    async def run(self) -> None:
        timeout = await sync_to_async(self._run)()
        await asyncio.sleep(timeout)
        if self.requeue:
            await self.task_queue.put(AlertTask(timeout, self.task_queue, requeue=True))
