import json

from django.conf import settings

from core import models
from core.helpers import update_timestamp, timestamp_expired

from kombu.mixins import ConsumerMixin, ConsumerProducerMixin


class BaseWorker(ConsumerProducerMixin):
    """ Base Worker class """

    def __init__(self, connection, queues):
        self.connection = connection
        self.queues = queues
        self.responses = []
#        self.responses = {
#            "PONG": self.pong,
#            "SUP": self.sup,
#            "CUP": self.cup,
#            "ACK": self.ask,
#            "NACK": self.nack,
#            "INFO": self.info
#        }

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=self.queues,
                         accept=['json', 'pickle'],
                         callbacks=[self.handle_message]
                         )]

    def handle_message(self, body, message):
        """ """
        try:
            device_type, device_uid, command = message.delivery_info.get('routing_key').split('.')[1:]
            _body = json.loads(body)
            if command not in self.responses:
                raise Exception
            else:
                parsed = dict(
                    device_type = device_type,
                    device_uid = device_uid,
                    command = command,
                    timestamp = _body.get('timestamp', 0),
                    task_id = _body.get('task_id'),
                    datahold = _body.get('datahold')
                )
                return parsed
        except Exception:
            # todo: should be reported to error queue
            pass

    def publish(self, payload, exchange, routing_key):
        self.producer.publish(
            payload,
            exchange=exchange,
            routing_key=routing_key,
            retry=True,
        )


class PingPongWorker(BaseWorker):

    """ Worker receives Pong """

    def handle_message(self, body, message):
        parsed = super().manage(body, message)
        if timestamp_expired(parsed['timestamp']):
            self.publish_for_update(parsed)
            message.ack()

    def publish_for_new_config(self, parsed):
        needed = ('device_type', 'device_uid')
        payload = {k:v for k,v in parsed.items() if k in needed}
        self.publish(payload=payload,
                     exchange='internal',
                     routing_key='CUP')


class SendConfigWorker(BaseWorker):

    """ Worker send config to clients (CUP) """

    def handle_message(self, body, message):
        parsed = super().handle_message(body, message)
        update_timestamp(parsed['device_type'], parsed['device_uid'])
        # update timestamp in database
        # get config from database
        # pack config to packet
        # pass packet to mqtt exchange
        # put task_id to task_id check queue


class AckNackWorker(BaseWorker):

    """ Worker checks task_id and mark it as success/fail """

    def handle_ack_message(self, body, message):
        """ handling ack message """
        pass
        # get task_id from payload
        # check if task_id exists in list of tasks
        # close task if ACK
        # retry and inform if NACK

    def handle_nack_message(self, body, message):
        """ handling ack message """
        pass
        # get task_id from payload
        # check if task_id exists in list of tasks
        # close task if ACK
        # retry and inform if NACK


# TODO: design how global state should be applied
# todo: how websocket should be informed (signals or what)
# todo:


class StateUpdateWorker(BaseWorker):

    """ Update database by data received from clients """

    def handle_sup_message(self, body, message):
        """ handling server update message """
        pass
        # check payload
        # update timestamp in database
        # update database from payload
        # inform websocket queue

    def handle_info_message(self, body, message):
        """ handling info message """
        pass
        # update timestamp in database
        # get rpc call from payload
        # apply rpc call (another queue?)
