from core.helpers import get_server_timestamp
from kombu import Message
from core.transport.config import SkabenQueue
from core.transport.queue_handlers import BaseHandler

__all__ = ['InternalHandler']


class InternalHandler(BaseHandler):

    incoming_mark = SkabenQueue.NEW.value
    keepalive_mark = 'pong'
    state_save_mark = 'sup'  # updates config from client to server
    state_mutate_mark = 'info'  # mutates state without direct config save
    client_update_mark = 'cup'  # update config from server to client

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

        if packet_type == self.keepalive_mark:
            self.dispatch_keepalive(
                body,
                routing_data
            )
        elif packet_type in (self.state_save_mark, self.state_mutate_mark):
            body['datahold'].update({"timestamp": body.get('timestamp', get_server_timestamp())})
            self.dispatch_server_state_update(
                body['datahold'],
                [SkabenQueue.STATE_UPDATE.value, device_type, device_uuid, packet_type]
            )
        elif packet_type == self.client_update_mark:
            self.dispatch_client_state_send(
                body,
                [SkabenQueue.CLIENT_UPDATE.value, device_type, device_uuid]
            )
        else:
            message.reject()
            return
        message.ack()

    def dispatch_keepalive(self, body: dict, routing_data: list):
        if body.get('timestamp', 0) <= get_server_timestamp():
            self.dispatch_client_state_send(
                body,
                [SkabenQueue.CLIENT_UPDATE.value, *routing_data[1:3]]
            )
        else:
            self.dispatch_server_state_update(
                {'timestamp': body.get('timestamp')},
                [SkabenQueue.STATE_UPDATE.value, *routing_data[1:3]]
            )

    def dispatch_server_state_update(self, data: dict, routing_data: list):
        self.producer.publish(
            data,
            exchange=self.config.internal_exchange,
            routing_key=self.get_routing_key(routing_data)
        )

    def dispatch_client_state_send(self, body, routing_data: list):
        data = {'hash': body.get('hash', '')}
        self.producer.publish(
            data,
            exchange=self.config.internal_exchange,
            routing_key=self.get_routing_key(routing_data)
        )

    @staticmethod
    def get_instance(model, uid):
        return model.objects.get(uid=uid)
