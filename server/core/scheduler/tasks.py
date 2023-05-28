from django.conf import settings
from skabenproto import PING
from server.core.helpers import get_server_timestamp
from server.core.transport.publish import get_interface
from server.alert.service import AlertService
import threading


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
        raise NotImplementedError("Subclasses must implement the start() method.")


class PingerTask(Task):

    def __init__(self, timeout: int):
        """
        Initializes the PingerTask.

        Args:
            timeout: Timeout value for the task.
        """
        super().__init__(timeout)
        self.publisher = get_interface()

    async def run(self) -> None:
        """
        Runs the pinger task by sending PING packets for each topic.
        """
        for topic in settings.SKABEN_DEVICE_TOPICS.keys():
            packet = PING(
                uid='all',
                topic=topic,
                timestamp=get_server_timestamp(),
            )
            self.publisher.send_mqtt_skaben(packet)


# class IncreaseAlertTask(Task):
#
#     def __init__(self, timeout: int):
#         super().__init__(timeout)
#         self.packet = {
#             ''
#         }
#
#     async def run(self):
#         """Decreases alert level"""
#         self.publisher.send
#
#
# class DecreaseAlertTask(IncreaseAlertTask):
#
#     def action(self):
#         current = self.service.get_state_current()
#         if current.auto_decrease:
#             self.service.change_alert_counter(current.modifier, increase=False, comment='auto decrease')
