import json
import logging
import multiprocessing as mp
import time
import traceback
from typing import Optional, Union
from django.core.exceptions import ObjectDoesNotExist

from actions.main import EventManager
from alert.models import get_current_alert_state, get_last_counter, get_borders
from core.helpers import fix_database_conn, get_task_id
from eventlog.serializers import EventSerializer
from device.models import Lock
from kombu import Connection, Exchange
from kombu.message import Message
from kombu.mixins import ConsumerProducerMixin
from skabenproto import CUP
from shape.models import SimpleConfig, AccessCode

logger = logging.getLogger('django')


class WorkerRunner(mp.Process):
    """worker process runner"""

    def __init__(self,
                 worker_class: ConsumerProducerMixin,
                 connection: Connection,
                 queues: list,
                 exchanges: dict,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.worker = worker_class(connection, queues, exchanges)

    def run(self):
        self.worker.run()


class BaseWorker(ConsumerProducerMixin):
    """abstract Worker class"""

    def __init__(self,
                 connection: Connection,
                 queues: list,
                 exchanges: dict):
        self.connection = connection
        self.queues = queues
        self.exchanges = exchanges

    def handle_message(self, body: Union[str, dict], message: Message) -> dict:
        """parse MQTT message to dict or return untouched if it's already dict

           only messages which comes with 'ask.*' routing key should be parsed
        """
        try:
            rk = message.delivery_info.get('routing_key').split('.')
            if rk[0] == 'ask':
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
                    parsed.update(**data)
                    if not parsed.get('timestamp'):
                        parsed['timestamp'] = data.get('datahold', {}).get('timestamp', 1)
                return parsed
            else:
                # just return already parsed message
                return body
        except Exception:
            raise

    def publish(self, payload: dict, exchange: Exchange, routing_key: str):
        """publish abstract method"""
        publish_with_producer(payload, exchange, routing_key, self.producer)

    @staticmethod
    def parse_json(json_data: Optional[str] = None) -> dict:
        """get dict from json"""
        if isinstance(json_data, dict):
            return json_data

        if not json_data:
            return {}

        try:
            return json.loads(json_data)
        except Exception:
            return f"{json_data}"

    @staticmethod
    def parse_basic(routing_key: str) -> dict:
        """get device parameters from topic name (routing key)"""
        device_type, device_uid, command = routing_key
        data = dict(device_type=device_type,
                    device_uid=device_uid,
                    command=command)
        return data

    def parse_smart(self, data: dict) -> dict:
        """get additional data-fields from smart device"""
        parsed = {'datahold': f'{data}'}
        if isinstance(data, dict):
            datahold = self.parse_json(data.get('datahold', {}))
            parsed = dict(
                timestamp=int(data.get('timestamp', 0)),
                task_id=data.get('task_id', 0),
                datahold=datahold,
                hash=data.get('hash', '')
            )
        return parsed

    def update_timestamp_only(self, parsed: dict, timestamp: Union[str, int] = None):
        timestamp = int(time.time()) if not timestamp else timestamp
        parsed['timestamp'] = timestamp
        parsed['datahold'] = {'timestamp': timestamp}
        parsed['command'] = 'sup'
        parsed['hash'] = parsed.get('hash', '')
        self.save_device_config(parsed)

    def push_device_config(self, parsed: dict):
        """send config to device (emulates config request from device'"""
        routing_key = f"{parsed['device_type']}.{parsed['device_uid']}.cup"
        self.publish(parsed,
                     exchange=self.exchanges.get('ask'),
                     routing_key=routing_key)

    def save_device_config(self, parsed: dict):
        """save device config by passing data to SaveWorker"""
        self.publish(parsed,
                     exchange=self.exchanges.get('internal'),
                     routing_key='save')

    def report(self, message: Union[dict, str], level: str = 'info'):
        """report message"""
        if not isinstance(message, dict):
            message = {'message': message}
        message.update(timestamp=int(time.time()))
        send_log(message, level)

    def report_error(self, message: str):
        """report unwanted behavior"""
        self.report(message, "error")

    def send_websocket(self, message: str, level: str = "info", access: str = "root"):
        """prepare data and send via _external_ `send_websocket` function"""
        event_type = 'websocket'
        payload = {
            "message": message,
            "level": level,
            "event_type": event_type,
            "timestamp": int(time.time()),
            "access": access,
        }
        return send_websocket(payload, level, access, self.producer)

    def get_consumers(self, consumer, channel):
        """setup consumer and assign callback"""
        _consumer = consumer(queues=self.queues,
                             accept=['json'],
                             callbacks=[self.handle_message])
        return [_consumer]

    def __str__(self):
        return f"{self.__class__.__name__}"


class LogWorker(BaseWorker):
    """log messages (events) worker"""

    def handle_message(self, body: Union[str, dict], message: Message):
        try:
            parsed = super().handle_message(body, message)
            level = message.delivery_info.get('routing_key', "info")

            # TODO: адресные логи, с source!
            data = dict(
                message={"log": parsed.get('message')},
                level=level,
                source=parsed.get('device_uid', 'log'),
                stream=parsed.get('device_type', 'log')
            )

            # self.send_to_endpoints(data)
            self.save_message(data)
            message.ack()
        except Exception as e:
            logger.exception(f"{self} when handling message: {e}")

    @staticmethod
    def send_to_endpoints(data):
        """send to websocket endpoint"""
        send_websocket(**data)

    @staticmethod
    def save_message(data: dict):
        """save message as log record"""
        serializer = EventSerializer(data=data)
        if serializer.is_valid():
            serializer.save()


class SaveWorker(BaseWorker):
    """Save worker"""

    smart = DEVICES

    def device_not_found(self, device_type: str, device_uid: str):
        """spawn notification about unregistered device"""
        raise NotImplementedError

    @fix_database_conn
    def handle_message(self, body: Union[str, dict], message: Message):
        """handling server update message

           save device state to database without sending update packet (CUP) back
           serializer context {"no_send": True} do the trick
        """
        try:
            parsed = super().handle_message(body, message)
            logger.debug(f'handling {body} {message}')
            message.ack()
            _type = parsed['device_type']
            _uid = parsed['device_uid']
            # include timestamp to load
            parsed['datahold'].update({"timestamp": parsed.get('timestamp', int(time.time()))})

            device = self.smart.get(_type)
            if not device:
                return

            # get device instance from DB
            try:
                device_instance = device['model'].objects.get(uid=_uid)
            except Exception as e:  # DoesNotExist - todo: make normal exception
                raise Exception(f"database error: {e}")

            data = parsed["datahold"]
            serializer = device["serializer"](device_instance,
                                              data=data,
                                              partial=True,
                                              context={"no_send": True})

            if serializer.is_valid():
                serializer.save()
                #filtered = {k: v for k, v in data.items() if k != "timestamp"}
                #if filtered:
                #    self.report(f"{_type} {_uid} updated - {filtered}")

        except Exception as e:
            self.report_error(f"{self} when handling message: {e}")


class PingPongWorker(BaseWorker):
    """Отвечает на ПОНГ, перенаправляет все в CUP очередь к SendConfigWorker,
       вскоре может быть выпилен насовсем.

       NOTE: all keep-alive timeouts are set in django.settings.APPCFG
    """

    def handle_message(self, body: Union[str, dict], message: Message):
        try:
            parsed = super().handle_message(body, message)
            message.ack()
            self.push_device_config(parsed)
        except Exception as e:
            self.report_error(f"{self} when handling message: {e}")


class SendConfigWorker(BaseWorker):
    """send config update to clients (CUP)"""

    smart = DEVICES

    @fix_database_conn
    def handle_message(self, body: Union[str, dict], message: Message):
        try:
            parsed = super().handle_message(body, message)
            device_type = parsed.get('device_type')
            device_uid = parsed.get('device_uid')
            message.ack()

            try:
                if device_type in SIMPLE:
                    return self.send_config_simple(device_type, device_uid)
                # достаем из базы актуальный конфиг устройства
                config = self.get_config(device_type, device_uid)
                # проверяем разницу хэшей в пришедшем конфиге и серверном
                if str(config.get('hash')) != str(parsed.get('hash', '')):
                    self.send_config(device_type, device_uid, config)
                else:
                    # обновляем таймстемп в любом случае
                    self.update_timestamp_only(parsed)
            except Exception as e:
                raise Exception(f"{body} {message} {parsed} {e}")
        except Exception as e:
            self.report_error(f"{self} when handling message: {e}")

    def get_config(self, device_type: str, device_uid: str) -> dict:
        device = self.smart.get(device_type)
        if not device:
            self.report_error(f"device not in smart list, but CUP received: {device_type}")
            return {}

        try:
            device_instance = device['model'].objects.get(uid=device_uid)
            serializer = device['serializer'](instance=device_instance)
            return serializer.data
        except Exception as e:  # DoesNotExist - fixme: make normal exception
            self.report_error(f"[DB error] {device_type} {device_uid}: {e}")

    def send_config(self, device_type: str, device_uid: str, config: dict):
        logger.debug(f'sending config for {device_type} {device_uid}')
        packet = CUP(
            topic=device_type,
            uid=device_uid,
            task_id=get_task_id(device_uid[-4:]),
            datahold=config,
            timestamp=int(time.time())
        )
        self.publish(packet.payload,
                     exchange=self.exchanges.get('mqtt'),
                     routing_key=f"{device_type}.{device_uid}.cup")

    @staticmethod
    def get_scl_config():
        borders = get_borders()
        last_counter = get_last_counter()
        if last_counter > borders[-1]:
            last_counter = borders[-1]
        elif last_counter < borders[0]:
            last_counter = borders[0]

        device_uid = 'all'
        datahold = {
            'borders': borders,
            'level': last_counter,
            'state': 'green'
        }
        return device_uid, datahold

    def send_config_simple(self, device_type: str, device_uid: Optional[str] = None):
        """Отправляем конфиг простым устройствам в соответствии с текущим уровнем тревоги"""
        datahold = {}

        if device_type != 'scl':
            state_id = get_current_alert_state()
            instance = SimpleConfig.objects.filter(dev_type=device_type, state__id=state_id).first()
            if not device_uid or device_type in ('pwr', 'hold'):
                device_uid = 'all'
            if not instance or not instance.config:
                return

            datahold = instance.config

        if device_type == 'scl':
            device_uid, datahold = self.get_scl_config()

        packet = CUP(
            topic=device_type,
            uid=device_uid,
            datahold=datahold,
            task_id='simple',
            timestamp=int(time.time())
        )

        self.publish(packet.payload,
                     exchange=self.exchanges.get('mqtt'),
                     routing_key=f"{device_type}.{device_uid}.cup")


class AckNackWorker(BaseWorker):
    """checks task_id and mark it as success/fail

       todo: work in process
    """

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
    """apply scenarios based on SUP/INFO messages"""

    def handle_message(self, body, message):
        try:
            parsed = super().handle_message(body, message)
            message.ack()
            if parsed.get("command", "").lower() == "sup":
                if parsed.get('device_type') not in SIMPLE:
                    self.save_device_config(parsed)
            else:
                data = {
                    "level": "info",
                    "stream": parsed['device_type'],
                    "source": parsed['device_uid'],
                    "message": parsed['datahold']
                }
                if parsed['device_type'] == 'lock' and data["message"].get('type') == 'access':
                    data["message"] = self.parse_access_log(
                        parsed['datahold'],
                        parsed['device_uid']
                    )
                serializer = EventSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()

            try:
                with EventManager() as manager:
                    manager.apply(parsed)
            except Exception:
                raise Exception(f"scenario cannot be applied: {traceback.format_exc()}")

        except Exception as e:
            self.report_error(f"{self} when handling message: {e}")

    @staticmethod
    def parse_access_log(message: dict, source: str):
        """Трансформирует код в данные обладателя или создает новую пустую запись карты если такого пользователя нет"""
        access_code = message.get("content")
        try:
            person = AccessCode.objects.filter(code=access_code).first()
            if not person:
                raise ObjectDoesNotExist
            lock = Lock.objects.filter(uid=source).first()
            success = "доступ разрешен" if message.get('success') else "доступ запрещен"
            result = f"{lock.info} : {success} : " + "{position} {name} {surname}".format(**person.__dict__)
            return {
                "type": "access_log",
                "content": result
            }
        except ObjectDoesNotExist:
            card_length = 6
            if card_length + 1 > len(str(access_code)) < card_length:
                return {
                    "type": "log",
                    "content": f"Код не является картой и его нет в базе - {access_code}"
                }
            instance = AccessCode(
                code=access_code,
                name=f"UNKNOWN",
                surname=f"UNKNOWN",
                position=f"{access_code} from {source}"
            )
            instance.save()
            return {
                "type": "log",
                "content": f"{instance.code} was AUTO-GENERATED from {source} at first time!"
            }