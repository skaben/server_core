from kombu import Message
from core.helpers import from_json
from core.transport.config import SkabenQueue, ASK_QUEUE
from core.transport.queue_handlers import BaseHandler

__all__ = ['TranslatorHandler']


class TranslatorHandler(BaseHandler):
    """
        Translates incoming messages from MQTT into internal format and pass to internal queue
    """

    incoming_mark = ASK_QUEUE
    outgoing_mark = SkabenQueue.NEW.value
    # types of packages with additional payload
    datahold_packet_mark = ['cup', 'sup', 'info']

    def handle_message(self, body: str | dict, message: Message) -> dict:
        routing_type, device_type, device_uuid, packet_type = message.delivery_info.get('routing_key').split('.')
        if routing_type != self.incoming_mark:
            # TODO: send error to log_error queue
            message.requeue()
            return

        try:
            payload_data = from_json(body)
            if packet_type in self.datahold_packet_mark:
                payload_data.update(self.parse_datahold(payload_data))
        except Exception as e:
            message.reject()
            raise Exception(f"cannot parse message payload `{body}` >> {e}")
        message.ack()
        self.producer.publish(
            payload_data,
            exchange=self.config.internal_exchange,
            routing_key=self.get_routing_key([self.outgoing_mark, device_type, device_uuid, packet_type])
        )

    @staticmethod
    def parse_datahold(data: dict) -> dict:
        result = {'datahold': f'{data}'}
        if isinstance(data, dict):
            result = dict(
                timestamp=int(data.get('timestamp', 0)),
                task_id=data.get('task_id', 0),
                hash=data.get('hash', ''),
                datahold=from_json(data.get('datahold', {}))
            )
        return result
