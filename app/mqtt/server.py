"""

    MQTT Router 2.0

    Estabilishing connection with Broker
    Start keepalive broadcast pinging
    Receive and publish messages

    TODO: migrated from old skaben, needs refactoring, too many code was hardcoded for last event

"""

import time
import json
import threading
from multiprocessing import Queue
import paho.mqtt.client as mqtt
import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

import skabenproto as sk

from django.conf import settings

channel_layer = get_channel_layer()
logger = logging.getLogger('skaben.sk_mqtts')

# separate MQTT server to shared

class MQTTPingLegacy(threading.Thread):

    def __init__(self, pub):
        super().__init__()
        self.pub = pub

    def run(self):
        print('start pinging legacy dumbs')
        self.kill = None
        while True:
            if self.kill:
                break
            try:
                for channel in ('RGB', 'PWR'):
                    with sk.PacketEncoder() as p:
                        packet = p.load('LEGPING',
                                        dev_type=channel)
                        encoded = p.encode(packet)
                        self.pub.put(encoded)
                    time.sleep(settings.APPCFG['timeout'] * 3)
            except:
                logger.exception('cannot send ping')


class MQTTPing(threading.Thread):

    def __init__(self, pub):
        super().__init__()
        self.pub = pub
        self.config = settings.APPCFG

    def run(self):
        print('start pinging')
        self.kill = None
        while True:
            if self.kill:
                break
            try:
                for channel in self.config['device_types']:
                    with sk.PacketEncoder() as p:
                        packet = p.load('PING',
                                          dev_type=channel)
                        encoded = p.encode(packet)
                        self.pub.put(encoded)
                    time.sleep(self.config['timeouts']['ping'])
            except:
                logger.exception('cannot send ping')


class MQTTServer(threading.Thread):

    """
        listen to mqttserver
        publish to mqttclient
        yeah, that simple
    """
    dumb_dict = dict()  # DUMB LEGACY
    rgb_send_conf = None  # DUMB LEGACY
    pwr_send_conf = None  # DUMB LEGACY

    def __init__(self, queue):
        super().__init__()
        self.running = False
        self.pub = queue
        self.cfg = settings.APPCFG
        self.client = None
        self.qos = 0  # set QoS level
        self.is_connected = False
        # mqtt channels
        self.publish_to = self.cfg['device_types']
        self.listen_to = [(c + 'ask' + '/#', self.qos)
                          for c in self.cfg['device_types']]
        # LEGACY: rgb
        self.listen_to.append(("RGBASK", self.qos))
        self.listen_to.append(("PWRASK", self.qos))
        #
        self.sub = []  # subscribed channels
        self.no_sub = []  # not subscribed channels
        # DUMB LEGACY
        self.dumb_timeout = int(self.cfg['timeouts']['ping'] * 5)

    def run(self):
        print('MQTT server starting...')
        self.running = True
        ping = MQTTPing(self.pub)
        ping_legacy = MQTTPingLegacy(self.pub)
        host = self.cfg['mqtt']['host']
        port = self.cfg['mqtt']['port']
        self.client = mqtt.Client(clean_session=True)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        try:
            self.client.connect(host=host,
                                port=port,
                                keepalive=settings.APPCFG['timeouts']['broker_keepalive'])
            logger.info(f'connecting to MQTT broker at {host}:{port}...')
            self.client.loop_start()
        except ConnectionRefusedError:
            logger.error(f'connection to {host}:{port} refused')
        except KeyboardInterrupt:
            raise SystemExit
        except BaseException:
            logger.exception('Exception in MQTT runner. exiting.')
            raise

        # main routine
        ping.start()
        ping_legacy.start()
        try:
            while self.running:
                if self.pub.empty():
                    time.sleep(.01)
                else:
                    message = self.pub.get()
                    if isinstance(message, tuple):
                        if not message[1].startswith('PING'):
                            if message[0].startswith("dumb"):
                                # LEGACY: rgb
                                self.send_dumb(message)
                        self.client.publish(*message)
                    else:
                        logger.error(f'bad message to publish: {message}')
        except KeyboardInterrupt:
            self.client.disconnect()
            raise SystemExit

    def on_message(self, client, userdata, msg):
        # RECEIVING
        try:
            # parsing dumb devices (LEGACY)
            # todo: should be rewrited
            if not msg.topic.startswith(('lock', 'term')):
                return self.receive_dumb(msg)
            with sk.PacketDecoder() as decoder:
                event = decoder.decode(msg)
                event.update({'type': 'device.event'})
                return self.send_event(event)
            #with PacketReceiver() as event:
            #    packet = event.create(msg)
            #    packet.update({'type': 'device.event'})
            #    async_to_sync(channel_layer.send)('events', packet)
        except:
            logger.exception(f'failed for {msg} :')
            raise

    def on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            logger.error(f'cannot connect to MQTT broker: {userdata} {flags} {rc}')
            return

        try:
            # control channels only
            self.subscribe(self.listen_to)
        except:
            logger.exception("subscription failed")
            self.client.on_disconnect()
        logger.info('mqtt connected!')
        self.is_connected = True

    def terminate(self):
        self.client.disconnect()
        self.running = False

    def on_disconnect(self):
        self.running = False

    def publish(self, message):
        """ Publish packed tuples """
        if not isinstance(message, tuple):
            raise Exception(f'bad message: {message}')
        else:
            logger.debug(f'publishing {message}')
            self.pub.put(message)

    def subscribe(self, channels):
        for channel in channels:
            r = self.client.subscribe(self.listen_to)
            if r[0] == 0:
                self.sub.append(channel)
            else:
                self.no_sub.append(channel)  # for later use
                logger.warning(f'failed to subscribe to {channel}')
        logger.info(f'subscribed to: {", ".join([s[0] for s in self.sub])}')

    def send_event(self, event):
        async_to_sync(channel_layer.send)('events', event)
        return True

    def send_aux(self, channel, msg):
        if channel not in self.cfg['device_types']:
            logging.error(f'aux channel not configured for {channel}')
            return
        logging.debug(f'sending control command to auxiliary channel: {msg}')
        cmd = json.loads(msg[1].split('/', 1)[1]).get('message')
        self.pub.put((channel, cmd))

    def send_dumb(self, msg):
        # DUMB LEGACY
        logging.debug(f'BROADCAST: {msg}')
        cmd = json.loads(msg[1].split('/', 1)[1]).get('config')
        if msg[0].endswith('rgb'):
            cmd_sequence = cmd.split()
            if not cmd_sequence:
                logger.error(f'dumb device config missing in {msg}')
            else:
                self.rgb_send_conf = False
                for cmd in cmd_sequence:
                    msg = ("RGB", '*' + cmd)#[1:]) # config string
                    time.sleep(.3)
                    print(msg)
                    self.pub.put(msg)
        elif msg[0].endswith('pwr'):
            self.pwr_send_conf = False
            self.pub.put(('PWR', cmd))
        elif msg[0].endswith('gas'):
            cmd_sequence = cmd.split()
            if not cmd_sequence:
                logger.error('gas send failed')
            else:
                for cmd in cmd_sequence:
                    msg = ("GAS", '*' + cmd)
                    time.sleep(.3)
                    print(msg)
                    self.pub.put(msg)

    def receive_dumb(self, msg):
        # DUMB LEGACY
        event = {'type': 'broadcast.event'}
        if msg.topic.startswith('PWRASK'):
            event['dev_type'] = 'pwr'
            if msg.payload.startswith(b'ASK'):
                event['payload'] = 'online'
            elif msg.payload.startswith(b'AUX'):
                event['payload'] = 'aux'
            elif msg.payload.startswith(b'PWR'):
                event['payload'] = 'pwr'
            elif msg.payload.endswith(b'PONG'):
                last_ts = self.dumb_dict.get('power')
                if last_ts and last_ts > int(time.time()) + int(self.dumb_timeout):
                    self.dumb_dict.update({'power': int(time.time())})
                    return True  # he's cool
                else:
                    self.dumb_dict.update({'power': int(time.time())})
                    event['payload'] = 'conf'
                    if self.pwr_send_conf:
                        # already sending config
                        return True
                    else:
                        self.pwr_send_conf = True
            return self.send_event(event)
        elif msg.topic.startswith('RGBASK'):
            if msg.payload.endswith(b'PONG'):
                event['dev_type'] = 'rgb'
                pong = msg.payload.decode('utf-8').split('/')
                duid = pong[0]
                ts = self.dumb_dict.get(duid)
                new_ts = int(time.time()) + int(self.dumb_timeout)
                if ts and int(ts) > int(time.time()):
                    self.dumb_dict.update({duid: new_ts})
                    return True
                else:
                    self.dumb_dict.update({duid: new_ts})
                    event['payload'] = 'conf'
                    if self.rgb_send_conf:
                        return True  # already sending config
                    else:
                        self.rgb_send_conf = True
                        return self.send_event(event)
        else:
            logging.warning(f'incoming event type: {msg}')


class ServerInterface:

    def __init__(self):
        self.queue = Queue()
        self.server_instance = None

    def start(self):
        try:
            if self.server_instance:
                if self.server_instance.running:
                    return 'server is already running'
                else:
                    self.server_instance.join(.1)
            self.server_instance = MQTTServer(queue=self.queue)
            self.server_instance.start()
            return f'server started: {self.server_instance}'
        except Exception:
            raise

    def stop(self):
        try:
            if self.server_instance.running:
                self.server_instance.terminate()
                self.server_instance.join(.1)
                return 'server stopped'
            else:
                return 'server already not operational'
        except Exception:
            raise

    def send(self, message):
        if not self.server_instance or not self.server_instance.running:
            raise Exception('server not running. start server for sending messages')
        else:
            try:
                self.server_instance.publish(message)
                return {'data': 'ok'}
            except Exception:
                raise


interface = ServerInterface()
