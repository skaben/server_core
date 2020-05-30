import json
import time
import logging

from kombu.mixins import ConsumerMixin, ConsumerProducerMixin
from django import db
from django.conf import settings

# todo: wtf timestamp in helpers
from core.helpers import update_timestamp, timestamp_expired
from core import models
from device import serializers as device_slr
from eventlog import serializers as eventlog_slr
from skabenproto import CUP, SUP

from random import randint

# TODO: less OOP, more mindfulness


def get_task_id():
    # todo: make actual task_id mechanism
    return ''.join([str(randint(0,9)) for _ in range(10)])


def fix_database_conn(func):
    """ django + kombu annoying bug fix """
    def wrapper(*args, **kwargs):
        for conn in db.connections.all():
            conn.close_if_unusable_or_obsolete()
        return func(*args, **kwargs)
    return wrapper


class BaseWorker(ConsumerProducerMixin):
    """ Base Worker class """

    def __init__(self, connection, queues, exchanges):
        self.connection = connection
        self.queues = queues
        self.exchanges = exchanges

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=self.queues,
                         accept=['json', 'pickle'],
                         callbacks=[self.handle_message]
                         )]

    def handle_message(self, body, message):
        """ """
        try:
            rk = message.delivery_info.get('routing_key').split('.')
            if rk[0] == 'ask':
                # only messages from mqtt comes with pre-device_type 'ask' routing key
                # and only this type of message should be parsed
                rk = rk[1:]
                device_type, device_uid, command = rk
                _body = json.loads(body)
                parsed = dict(
                    device_type=device_type,
                    device_uid=device_uid,
                    command=command,
                    timestamp=int(_body.get('timestamp', 0)),
                    task_id=_body.get('task_id'),
                    datahold=_body.get('datahold')
                )
                return parsed
            else:
                # just return already parsed dict
                return body
        except Exception as e:
            # todo: should be reported to error queue
            self.report_error(f"{e}")

    def publish(self, payload, exchange, routing_key):
        self.producer.publish(
            payload,
            exchange=exchange,
            routing_key=routing_key,
            retry=True,
        )

    def update_timestamp_only(self, parsed, timestamp=None):
        routing_key = f"{parsed['device_type']}.{parsed['device_uid']}.SUP"
        timestamp = int(time.time()) if not timestamp else timestamp
        parsed['timestamp'] = timestamp
        parsed['datahold'] = {"timestamp": timestamp}  # strip datahold for expired timestamp cases
        self.publish(parsed,
                     exchange=self.exchanges.get('ask'),
                     routing_key=routing_key)

    def report(self, message, routing_key='message'):
        """ report message """
        self.publish(message,
                     exchange=self.exchanges.get('log'),
                     routing_key=routing_key)

    def report_error(self, message):
        """ report exceptions or unwanted behavior """
        self.report(message, "error")

    def device_not_found(self, device_type, device_uid):
        self.publish({'device_type': device_type, 'device_uid': device_uid},
                     exchange=self.exchanges.get('internal'),
                     routing_key='new_device')


class LogWorker(BaseWorker):

    def handle_message(self, body, message):
        """ pass """
        try:
            event_data = {"event_type": "message",
                          "message": f"{body}"}
            logging.error(event_data)
            new_event = eventlog_slr.EventLogSerializer.create(event_data)
            new_event.save()
            #self.report_error(f"{event_data}")
        except Exception as e:
            self.report_error(f"{e}")
        message.ack()

class PingPongWorker(BaseWorker):

    """ Worker receives Pong """

    def handle_message(self, body, message):
        parsed = super().handle_message(body, message)
        _type = parsed['device_type']
        _uid = parsed['device_uid']
        if timestamp_expired(parsed['timestamp']):
            self.push_device_config(_type, _uid)
        else:
            self.update_timestamp_only(parsed)
        message.ack()

    def push_device_config(self, device_type, device_uid):
        routing_key = f"{device_type}.{device_uid}.CUP"
        self.publish('ping_pong_worker says',
                     exchange=self.exchanges.get('ask'),
                     routing_key=routing_key)


class SendConfigWorker(BaseWorker):

    """ Worker send config to clients (CUP) """

    def handle_message(self, body, message):
        parsed = super().handle_message(body, message)
        message.ack()
        _type = parsed['device_type']
        _uid = parsed['device_uid']
        self.update_timestamp_only(parsed)

    def send_config(self, device_type, device_uid, config):
        task_id = get_task_id()
        config = {"main": "test"}
        packet = CUP(
            topic=device_type,
            uid=device_uid,
            task_id=task_id,
            datahold=config,
            timestamp=int(time.time())
        )
        self.publish(packet.payload,
                     exchange=self.exchanges.get('mqtt'),
                     routing_key=packet.topic)


class AckNackWorker(BaseWorker):

    """ Worker checks task_id and mark it as success/fail """

    def handle_message(self):
        pass

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

    smart = settings.APPCFG.get('smart_devices')

    def handle_message(self, body, message):
        parsed = super().handle_message(body, message)
        _cmd = parsed['command']
        message.ack()

        if _cmd == 'INFO':
            self.handle_info_message(parsed)
        else:
            self.handle_sup_message(parsed)

    @fix_database_conn
    def handle_sup_message(self, parsed):
        """ handling server update message """
        _type = parsed['device_type']
        _uid = parsed['device_uid']
        # include timestamp to load
        parsed['datahold'].update({"timestamp": parsed['timestamp']})

        device_classname = self.smart.get(_type)
        if not device_classname:
            return self.report_error(f"received SUP not from smart device: {_type}")
        # get model class
        model_class = getattr(models, device_classname)
        # get device instance from DB
        try:
            device_instance = model_class.objects.get(uid=_uid)
        except Exception as e:  # DoesNotExist - todo: make normal exception
            #self.device_not_found(_type, _uid)
            return self.report_error(f"device {_type} {_uid} not found in DB: {e}")

        # get serializer
        serializer_class = getattr(device_slr, f"{device_classname}Serializer")

        if not serializer_class:
            return self.report_error(f'no serializer for: {_type}')

        serializer = serializer_class(device_instance,
                                          data=parsed['datahold'],
                                          partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return self.report_error(f'error when saving {_type} {_uid} > {serializer.errors}')
        # just testing logging
        #self.report(f"device {device_instance} new data {parsed['datahold']}")
        # TODO: inform websockets

    def handle_info_message(self, parsed):
        """ handling info message """
        pass
        # update timestamp in database
        # get rpc call from payload
        # apply rpc call (another queue?)
