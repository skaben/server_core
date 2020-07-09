import json
import time
import logging

from kombu.mixins import ConsumerMixin, ConsumerProducerMixin
from django import db
from django.conf import settings

# todo: wtf timestamp in helpers
from core.helpers import update_timestamp, timestamp_expired, dummy_context
from core import models
from device import serializers as device_serializer
from eventlog import serializers as eventlog_serializer
from skabenproto import CUP, SUP

from random import randint


def get_task_id(name='task'):
    num = ''.join([str(randint(0,9)) for _ in range(10)])
    return f"{name}-{num}"


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
                _body = json.loads(body) if body else {}
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

    def report(self, message, routing_key='info'):
        """ report message """
        self.publish({"message": message},
                     exchange=self.exchanges.get('log'),
                     routing_key=routing_key)

    def report_error(self, message):
        """ report exceptions or unwanted behavior """
        self.report(message=message,
                    routing_key="error")

    def send_websocket(self, message, event_type="system", level="info"):
        self.publish(payload={
                      "message": message,
                      "level": level,
                      "event_type": event_type,
                      "timestamp": int(time.time()),
                     },
                     exchange=self.exchanges.get("internal"),
                     routing_key="websocket")

    def device_not_found(self, device_type, device_uid):
        self.publish({'device_type': device_type, 'device_uid': device_uid},
                     exchange=self.exchanges.get('internal'),
                     routing_key='new_device')


class LogWorker(BaseWorker):

    def handle_message(self, body, message):
        level = message.delivery_info.get('routing_key', "info")
        event_type = body.get("event_type", "system")
        payload = body.get("message")

        self.send_websocket(message=payload,
                            level=level,
                            event_type=event_type)
        message.ack()


class PingPongWorker(BaseWorker):

    """ Worker receives Pong """

    def handle_message(self, body, message):
        parsed = super().handle_message(body, message)
        if timestamp_expired(parsed['timestamp']):
            self.push_device_config(parsed)
        else:
            self.update_timestamp_only(parsed)
        message.ack()

    def push_device_config(self, parsed):
        routing_key = f"{parsed['device_type']}.{parsed['device_uid']}.CUP"
        self.publish(parsed,
                     exchange=self.exchanges.get('ask'),
                     routing_key=routing_key)


class SendConfigWorker(BaseWorker):

    """ Worker send config to clients (CUP) """

    smart = settings.APPCFG.get('smart_devices')

    def handle_message(self, body, message):
        parsed = super().handle_message(body, message)
        message.ack()
        try:
            self.update_timestamp_only(parsed)
            self.send_config(parsed)
        except Exception as e:
            self.report_error(f"error: {e} {parsed}")

    def get_config(self, parsed):
        device_type = parsed.get('device_type')
        device_uid = parsed.get('device_uid')
        device_classname = self.smart.get(device_type)
        if not device_classname:
            return self.report_error(f"device not in smart list, but CUP received: {device_type}")
        # get model class
        model_class = getattr(models, device_classname)
        # get device instance from DB
        try:
            device_instance = model_class.objects.get(uid=device_uid)
            serializer_class = getattr(device_serializer, f"{device_classname}Serializer")
            ser = serializer_class(instance=device_instance,
                                   context=dummy_context)
            return ser.data
        except Exception as e:  # DoesNotExist - fixme: make normal exception
            return self.report_error(f"device {device_type} {device_uid} not found in DB: {e}")

    def send_config(self, parsed):
        device_type = parsed.get('device_type')
        device_uid = parsed.get('device_uid')
        packet = CUP(
            topic=device_type,
            uid=device_uid,
            task_id=get_task_id(device_uid[-4:]),
            datahold=self.get_config(parsed),
            timestamp=int(time.time())
        )
        self.publish(packet.payload,
                     exchange=self.exchanges.get('mqtt'),
                     routing_key=f"{device_type}.{device_uid}.CUP")


class AckNackWorker(BaseWorker):

    """ Worker checks task_id and mark it as success/fail """

    def handle_message(self, body, message):
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
        _cmd = parsed.get('command')
        message.ack()

        try:
            if _cmd == 'INFO':
                self.handle_info_message(parsed)
            else:
                self.handle_sup_message(parsed)
        except Exception as e:
            self.report_error(f"{e}")

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
        serializer_class = getattr(device_serializer, f"{device_classname}Serializer")

        if not serializer_class:
            return self.report_error(f'no serializer for: {_type}')

        serializer = serializer_class(device_instance,
                                      data=parsed['datahold'],
                                      partial=True,
                                      context=dummy_context)
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

