from django.conf import settings
from asgiref.sync import sync_to_async

from skabenproto import PING
from server.core.helpers import get_server_timestamp
from server.core.transport.publish import get_interface
from server.alert.service import AlertService


class Task:

    def __init__(self, timeout: int):
        """
        Initializes the Task.

        Args:
            timeout: Timeout value for the task.
        """
        self.timeout = timeout

    async def run(self) -> None:
        """
        Starts the task.
        """
        raise NotImplementedError("Subclasses must implement the run() method.")


class PingerTask(Task):

    def __init__(self, timeout: int):
        """
        Initializes the PingerTask.

        Args:
            timeout: Timeout value for the task.
        """
        super().__init__(timeout)

    def _run(self) -> None:
        """
            Runs the pinger task by sending PING packets for each topic.
        """
        with get_interface() as publisher:
            for topic in settings.SKABEN_DEVICE_TOPICS.keys():
                packet = PING(
                    uid='all',
                    topic=topic,
                    timestamp=get_server_timestamp(),
                )
                publisher.send_mqtt_skaben(packet)
    
    async def run(self) -> None:
        await sync_to_async(self._run)()


class AlertTask(Task):
    
    increase: bool

    def __init__(self, timeout: int):
        """Инициализация авто-изменения уровня тревоги.

        Args:
            timeout: регулярность запуска задачи
        """
        super().__init__(timeout)

    def _run(self) -> None:
        with AlertService() as service:
            current = service.get_state_current()

            if not current.ingame:
                return
            
            if current.auto_decrease and current.counter_decrease > 0:
                service.change_alert_counter(
                    current.counter_decrease,
                    increase=False,
                    comment=f'auto decrease by {current.counter_decrease}'
                )
            
            if current.auto_increase and current.counter_increase > 0:
                service.change_alert_counter(
                    current.counter_increase,
                    increase=True,
                    comment=f'auto increase by {current.counter_increase}'
                )

    async def run(self) -> None:
        await sync_to_async(self._run)()