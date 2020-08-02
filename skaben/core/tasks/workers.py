import json
import time
import multiprocessing as mp

from django import db
from django.conf import settings

from kombu.mixins import ConsumerProducerMixin

from core import models
from core.helpers import timestamp_expired
from scenario.default import scenario

from device.services import DEVICES
from skabenproto import CUP

from random import randint


def get_task_id(name='task'):
    num = ''.join([str(randint(0, 9)) for _ in range(10)])
    return f"{name}-{num}"


def fix_database_conn(func):
    """ django + kombu annoying bug fix """
    def wrapper(*args, **kwargs):
        for conn in db.connections.all():
            conn.close_if_unusable_or_obsolete()
        return func(*args, **kwargs)
    return wrapper


class WorkerRunner(mp.Process):

    def __init__(self, worker_class, connection, queues, exchanges, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.worker = worker_class(connection, queues, exchanges)

    def run(self):
        self.worker.run()


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

    def parse_smart(self, data):
        parsed = dict(
            timestamp=int(data.get('timestamp', 0)),
            task_id=data.get('task_id'),
            datahold=data.get('datahold'),
        )
        return parsed

    def handle_message(self, body, message):
        """ """
        try:
            rk = message.delivery_info.get('routing_key').split('.')
            if rk[0] == 'ask':
                # only messages from mqtt comes with pre-device_type 'ask' routing key
                # and only this type of message should be parsed
                try:
                    rk = rk[1:]
                    device_type, device_uid, command = rk
                except Exception as e:
                    raise Exception(f"cannot parse routing key `{rk}` >> {e}")

                try:
                    parsed = dict(
                        device_type = device_type,
                        device_uid = device_uid,
                        command = command
                    )
                    data = json.loads(body) if body else {}
                except Exception as e:
                    raise Exception(f"cannot parse message payload `{body}` >> {e}")

                # todo: singleton smart devices list
                if device_type in ['lock', 'terminal']:
                    parsed.update(self.parse_smart(data))
                else:
                    parsed.update({"datahold": data})
                return parsed
            else:
                # just return already parsed dict
                return body
        except Exception as e:
            self.report_error(f"when handling message: {e}")

    def publish(self, payload, exchange, routing_key):
        self.producer.publish(
            payload,
            exchange=exchange,
            routing_key=routing_key,
            retry=True,
        )

    def update_timestamp_only(self, parsed, timestamp=None):
        # todo: needs refactoring, bad assembling of SUP packet
        routing_key = f"{parsed['device_type']}.{parsed['device_uid']}.SUP"
        timestamp = int(time.time()) if not timestamp else timestamp
        parsed['timestamp'] = timestamp
        parsed['datahold'] = {"timestamp": timestamp}
        parsed['command'] = "SUP"
        self.publish(parsed,
                     exchange=self.exchanges.get('ask'),
                     routing_key=routing_key)

    def push_device_config(self, parsed):
        routing_key = f"{parsed['device_type']}.{parsed['device_uid']}.CUP"
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


class SaveConfigWorker(BaseWorker):

    """ Update database by data received from clients """

    smart = DEVICES

    @fix_database_conn
    def handle_message(self, body, message):
        """ handling server update message """
        parsed = super().handle_message(body, message)
        message.ack()
        _type = parsed['device_type']
        _uid = parsed['device_uid']
        # include timestamp to load
        parsed['datahold'].update({"timestamp": parsed.get('timestamp', int(time.time()))})

        device = self.smart.get(_type)
        if not device:
            return self.report_error(f"received SUP from unknown device type: {_type}")

        # get device instance from DB
        try:
            device_instance = device['model'].objects.get(uid=_uid)
        except Exception as e:  # DoesNotExist - todo: make normal exception
            #self.device_not_found(_type, _uid)
            return self.report_error(f"device {_type} {_uid} not found in DB: {e}")

        serializer = device["serializer"](device_instance,
                                          data=parsed["datahold"],
                                          partial=True)

        if serializer.is_valid():
            serializer.save()


class SendConfigWorker(BaseWorker):
    """ Worker send config to clients (CUP) """

    smart = DEVICES

    def handle_message(self, body, message):
        parsed = super().handle_message(body, message)
        device_type = parsed.get('device_type')
        device_uid = parsed.get('device_uid')
        message.ack()
        try:
            self.update_timestamp_only(parsed)
            self.send_config(device_type, device_uid)
        except Exception as e:
            self.report_error(f"error: {e} {body} {message} {parsed}")

    def get_config(self, device_type, device_uid):
        device = self.smart.get(device_type)
        if not device:
            return self.report_error(f"device not in smart list, but CUP received: {device_type}")

        try:
            device_instance = device['model'].objects.get(uid=device_uid)
            ser = device['serializer'](instance=device_instance)
            return ser.data
        except Exception as e:  # DoesNotExist - fixme: make normal exception
            return self.report_error(f"device {device_type} {device_uid} not found in DB: {e}")

    def send_config(self, device_type, device_uid):
        packet = CUP(
            topic=device_type,
            uid=device_uid,
            task_id=get_task_id(device_uid[-4:]),
            datahold=self.get_config(device_type, device_uid),
            timestamp=int(time.time())
        )
        self.publish(packet.payload,
                     exchange=self.exchanges.get('mqtt'),
                     routing_key=f"{device_type}.{device_uid}.CUP")


class AckNackWorker(BaseWorker):

    """ Worker checks task_id and mark it as success/fail """

    def handle_message(self, body, message):
        message.ack()

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


class StateUpdateWorker(BaseWorker):

    def handle_message(self, body, message):
        """ handling state update messages """
        parsed = super().handle_message(body, message)
        message.ack()
        #scenario.new(parsed)

        # update timestamp in database
        # get rpc call from payload
        # apply rpc call (another queue?)
