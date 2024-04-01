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

    def __init__(self, timeout: int, increase: bool):
        """Инициализация авто-изменения уровня тревоги.

        Args:
            timeout: регулярность запуска задачи
            increase: увеличивать или уменьшать уровень тревоги
        """
        super().__init__(timeout)

        self.increase = increase
        with AlertService() as service:
            states = service.get_ingame_states()
            self.boundaries = [states.first().threshold, states.last().threshold]

    def _run(self) -> None:
        with AlertService() as service:
            current = service.get_state_current()
            counter = service.get_last_counter()

            if not current.ingame or counter not in self.boundaries:
                return
            
            val = current.modifier

            if not self.increase and current.auto_decrease:
                service.change_alert_counter(val, increase=False, comment=f'auto decrease by {val}')
            
            if self.increase and current.auto_increase:
                service.change_alert_counter(val, increase=True, comment=f'auto increase by {val}')

    async def run(self) -> None:
        await sync_to_async(self._run)()
