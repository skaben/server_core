import json
import time
import multiprocessing as mp

from django.conf import settings

from kombu.mixins import ConsumerProducerMixin

from core import models
from core.helpers import timestamp_expired, fix_database_conn, get_task_id
from scenario.main import scenario

from skabenproto import CUP
from device.services import DEVICES
from transport.interfaces import send_log

from random import randint


class WorkerRunner(mp.Process):

    """ Worker process wrapper """

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

    def parse_smart(self, data):
        parsed = dict(
            timestamp=int(data.get('timestamp', 0)),
            task_id=data.get('task_id'),
            datahold=data.get('datahold'),
        )
        return parsed

    def handle_message(self, body, message):
        """ Parse MQTT message to dict or return untouched if already dict """
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
        timestamp = int(time.time()) if not timestamp else timestamp
        parsed['timestamp'] = timestamp
        parsed['datahold'] = {"timestamp": timestamp}
        parsed['command'] = "SUP"
        self.save_device_config(parsed)

    def push_device_config(self, parsed):
        routing_key = f"{parsed['device_type']}.{parsed['device_uid']}.CUP"
        self.publish(parsed,
                     exchange=self.exchanges.get('ask'),
                     routing_key=routing_key)

    def save_device_config(self, parsed):
        self.publish(parsed,
                     exchange=self.exchanges.get('internal'),
                     routing_key="save")

    def report(self, message, level='info'):
        """ report message """
        send_log(message, level)

    def report_error(self, message):
        """ report exceptions or unwanted behavior """
        send_log(message, "error")

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
        """ Spawn notification to front about new device """
        pass


class LogWorker(BaseWorker):

    """ Worker log messages """

    def handle_message(self, body, message):
        level = message.delivery_info.get('routing_key', "info")
        event_type = body.get("event_type", "system")
        payload = body.get("message")

        self.send_websocket(message=payload,
                            level=level,
                            event_type=event_type)
        message.ack()


class SaveWorker(BaseWorker):

    """ Worker updates database """

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


class PingPongWorker(BaseWorker):

    """ Worker receives PONG, updates timestamp or send back config """

    def handle_message(self, body, message):
        parsed = super().handle_message(body, message)
        if timestamp_expired(parsed['timestamp']):
            self.push_device_config(parsed)
        else:
            self.update_timestamp_only(parsed)
        message.ack()


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

    """ Worker apply scenarios based on SUP/INFO messages """

    def handle_message(self, body, message):
        parsed = super().handle_message(body, message)
        message.ack()
        scenario.new(parsed)
        self.save_device_config(parsed)
        # update timestamp in database
        # get rpc call from payload
        # apply rpc call (another queue?)
