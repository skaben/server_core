from core.helpers import get_server_time
from kombu import Message
from core.transport.config import SkabenQueue
from core.transport.handlers import BaseHandler

__all__ = ['InternalHandler']


class InternalHandler(BaseHandler):

    incoming_mark = SkabenQueue.NEW.value
    keepalive_mark = ['pong']
    state_update_mark = ['sup', 'info']
    client_update_mark = ['cup']

    def handle_message(self, body: dict, message: Message):
        """Ignoring message, body already has all information we needed"""
        routing_data = [
            incoming_mark,
            device_type,
            device_uuid,
            packet_type
        ] = message.delivery_info.get('routing_key').split('.')
        if incoming_mark != self.incoming_mark:
            message.requeue()
            return

        if packet_type in self.keepalive_mark:
            self.handle_ping(
                body,
                routing_data
            )
        elif packet_type in self.state_update_mark:
            body['datahold'].update({"timestamp": body.get('timestamp', get_server_time())})
            self.handle_server_state_update(
                body['datahold'],
                [SkabenQueue.STATE_UPDATE.value, device_type, device_uuid]
            )
        elif packet_type in self.client_update_mark:
            self.handle_send_client_state(
                body,
                [SkabenQueue.CLIENT_UPDATE.value, device_type, device_uuid]
            )
        else:
            message.reject()
            return
        message.ack()

    def handle_ping(self, body: dict, routing_data: list):
        if body.get('timestamp', 0) <= get_server_time():
            self.handle_send_client_state(
                body,
                [SkabenQueue.CLIENT_UPDATE.value, *routing_data[1:3]]
            )
        else:
            self.handle_server_state_update(
                {'timestamp': body.get('timestamp')},
                [SkabenQueue.STATE_UPDATE.value, *routing_data[1:3]]
            )

    def handle_server_state_update(self, data: dict, routing_data: list):
        self.producer.publish(
            data,
            exchange=self.config.internal_exchange,
            routing_key=self.get_routing_key(routing_data)
        )

    def handle_send_client_state(self, body, routing_data: list):
        data = {'hash': body.get('hash', '')}
        self.producer.publish(
            data,
            exchange=self.config.internal_exchange,
            routing_key=self.get_routing_key(routing_data)
        )

    @staticmethod
    def get_instance(model, uid):
        return model.objects.get(uid=uid)
