import json
import time
import traceback
import multiprocessing as mp

from kombu.mixins import ConsumerProducerMixin

from core.helpers import timestamp_expired, fix_database_conn, get_task_id
from scenario.main import scenario

from skabenproto import CUP
from device.services import DEVICES
from eventlog.serializers import EventLogSerializer
from transport.interfaces import send_websocket, send_log, publish_with_producer


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

    def handle_message(self, body, message):
        """ Parse MQTT message to dict or return untouched if already dict """
        try:
            rk = message.delivery_info.get('routing_key').split('.')
            if rk[0] == 'ask':
                # only messages from mqtt comes with 'ask.*' routing key
                # only this type of message should be parsed
                try:
                    rk = rk[1:]
                except Exception as e:
                    raise Exception(f"cannot parse routing key `{rk}` >> {e}")

                try:
                    parsed = self.parse_basic(rk)
                    data = self.parse_json(body)
                except Exception as e:
                    raise Exception(f"cannot parse message payload `{body}` >> {e}")

                # todo: singleton smart devices list
                if parsed.get("device_type") in ['lock', 'terminal']:
                    parsed.update(self.parse_smart(data))
                else:
                    parsed.update({"datahold": data})
                return parsed
            else:
                # messages not from mqtt is already parsed
                return body
        except Exception:
            raise

    def publish(self, payload, exchange, routing_key):
        publish_with_producer(payload, exchange, routing_key, self.producer)

    def parse_json(self, json_data=None):
        if isinstance(json_data, dict) or not json_data:
            return json_data

        try:
            return json.loads(json_data)
        except Exception:
            return f"{json_data}"


    def parse_basic(self, routing_key):
        device_type, device_uid, command = routing_key
        return dict(device_type=device_type,
                    device_uid=device_uid,
                    command=command)

    def parse_smart(self, data):
        parsed = f"{data}"
        if isinstance(data, dict):
            parsed = dict(
                timestamp=int(data.get('timestamp', 0)),
                task_id=data.get('task_id'),
                datahold=self.parse_json(data.get('datahold')),
            )
        return parsed

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

    def device_not_found(self, device_type, device_uid):
        """ Spawn notification to front about new device """
        raise NotImplementedError

    def report(self, message, level='info'):
        """ report message """
        if not isinstance(message, dict):
            message = {"message": message}
        send_log(message, level, self.producer)

    def report_error(self, message):
        """ report exceptions or unwanted behavior """
        self.report(message, "error")

    def send_websocket(self, message, level="info", access="root"):
        payload = {
            "message": message,
            "level": level,
            "event_type": event_type,
            "timestamp": int(time.time()),
            "access": access,
        }
        return send_websocket(payload, level, access, self.producer)

    def get_consumers(self, Consumer, channel):
        """ Setup consumer and assign callback """
        consumer = Consumer(queues=self.queues,
                            accept=['json'],
                            callbacks=[self.handle_message])
        return [consumer]

    def __str__(self):
        return f"{self.__class__.__name__}"


class LogWorker(BaseWorker):

    """ Worker log messages """

    def handle_message(self, body, message):
        try:
            parsed = super().handle_message(body, message)
            access = "root"
            level = message.delivery_info.get('routing_key', "info")
            payload = parsed.get("message")
            if parsed.get("access"):
                access = parsed.pop("access")

            data = dict(
                message=payload,
                level=level,
                access=access
            )

            serializer = EventLogSerializer(data=data)
            if serializer.is_valid():
                serializer.save()

            send_websocket(**data)
            message.ack()
        except Exception as e:
            self.report_error(f"{self} when handling message: {e}")


class SaveWorker(BaseWorker):

    """ Worker updates database """

    smart = DEVICES

    @fix_database_conn
    def handle_message(self, body, message):
        """ handling server update message """
        try:
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
        except Exception as e:
            self.report_error(f"{self} when handling message: {e}")


class PingPongWorker(BaseWorker):

    """ Worker receives PONG, updates timestamp or send back config """

    def handle_message(self, body, message):
        try:
            parsed = super().handle_message(body, message)
            if timestamp_expired(parsed['timestamp']):
                self.push_device_config(parsed)
            else:
                self.update_timestamp_only(parsed)
            message.ack()
        except Exception as e:
            self.report_error(f"{self} when handling message: {e}")


class SendConfigWorker(BaseWorker):
    """ Worker send config to clients (CUP) """

    smart = DEVICES

    def handle_message(self, body, message):
        try:
            parsed = super().handle_message(body, message)
            device_type = parsed.get('device_type')
            device_uid = parsed.get('device_uid')
            message.ack()
            try:
                self.update_timestamp_only(parsed)
                self.send_config(device_type, device_uid)
            except Exception as e:
                raise Exception(f"{e} {body} {message} {parsed}")
        except Exception as e:
            self.report_error(f"{self} when handling message: {e}")

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
        config = self.get_config(device_type, device_uid)
        if not config:
            return self.report_error(f"device {device_type} uid {device_uid} missing in database")
            #return self.device_not_found(device_type, device_uid)

        packet = CUP(
            topic=device_type,
            uid=device_uid,
            task_id=get_task_id(device_uid[-4:]),
            datahold=config,
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
        try:
            parsed = super().handle_message(body, message)
            message.ack()

            ident = f"{parsed['device_type']}_{parsed['device_uid']} {parsed['command']}"

            if parsed.get("command") == "SUP":
                self.save_device_config(parsed)
                comment = "config updated"
            else:
                comment = "new info message"

            #try:
            #    scenario.new(parsed)
            #except Exception:
            #    raise Exception(f"scenario cannot be applied: {traceback.format_exc()}")

            self.report(f"{ident} {comment} - {parsed}")
        except Exception as e:
            self.report_error(f"{self} when handling message: {e}")
