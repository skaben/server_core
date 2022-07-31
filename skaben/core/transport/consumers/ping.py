from .default import QueueConsumer
from kombu import Message


class PingConsumer(BaseConsumer):

    def handle(self, body: str | dict, message: Message) -> dict:
        message.ack()
        try:
            parsed = super().handle(body, message)
            # self.push_device_config(parsed)
        except Exception as e:
            raise
            # self.report_error(f"{self} when handling message: {e}")

