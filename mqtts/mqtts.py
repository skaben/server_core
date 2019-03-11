"""

    MQTT Router 2.0

    Estabilishing connection with Broker
    Start keepalive broadcast pinging
    Receiving and publishing messages

"""

import time
import threading
from multiprocessing import Queue
import paho.mqtt.client as mqtt
import logging as logger

from mqtts.config import config
from mqtts.contexts import PacketSender, PacketReceiver


class MQTTServer:

    """
        listen to mqttserver
        publish to mqttclient
        yeah, that simple
    """

    def __init__(self, config, queue):
        self.disabled = True
        self.pub = queue
        self.config = config
        self.client = None
        qos = 0  # set QoS level
        self.is_connected = False
        # mqtt channels
        self.publish_to = self.config.dev_types
        self.listen_to = [(c + 'ask' + '/#', qos)
                          for c in self.config.dev_types]
        self.sub = []  # subscribed channels
        self.no_sub = []  # not subscribed channels

    def enable(self):
        self.disabled = None
        msg = 'MQTT server start'
        self.main = threading.Thread(target=self.run,
                                     name='mqtt_main',
                                     daemon=True)
        self.main.start()
        self.ping = threading.Thread(target=self._ping,
                                     name='mqtt_ping',
                                     daemon=True)
        self.ping.start()
        print(msg)
        return msg

    def run(self):
        host = self.config.mqtt['host']
        port = self.config.mqtt['port']
        self.client = mqtt.Client(clean_session=True)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        try:
            self.client.connect(host=host,
                                port=port,
                                keepalive=self.config.timeout['mqtt'])
            logger.info(f'connecting to MQTT broker at {host}:{port}...')
            self.client.loop_start()
        except ConnectionRefusedError:
            logger.error(f'connection to {host}:{port} refused')
        except KeyboardInterrupt:
            raise SystemExit
        except BaseException:
            logger.exception('Exception in MQTT runner. exiting.')
            raise

        logger.info(f'subscribed to: {", ".join([s[0] for s in self.sub])}')

        # main routine
        print('MQTT server started')
        try:
            while True:
                if self.disabled:
                    break
                if self.pub.empty():
                    time.sleep(.01)
                else:
                    message = self.pub.get()
                    if isinstance(message, tuple):
                        if not message[1].startswith('PING'):
                            logger.debug(f'publishing {message}')
                        self.client.publish(*message)
                    else:
                        logger.error(f'bad message to publish: {message}')
        except KeyboardInterrupt:
            self.client.disconnect()
            raise SystemExit

    def on_message(self, client, userdata, msg):
        # RECEIVING
        try:
            with PacketReceiver() as event:
                packet = event.create(msg)
                if packet['command'] in ('ACK', 'NACK'):
                    # close existing job, not affected by ts
                    print(packet['task_id'], 'received!')
                    logger.warning(f'not implemented yet: {event}')
                    return
                #if event.ts + config.timeout['alive'] < int(time.time()):
                else:
                    # enqueue new job
                    try:
                        print(packet)
                    #    CSE = self.config.task_clientside
                    #    t = CSE.enqueue(device_task,
                    #                     packet,
                    #                     ttl=self.config.rq['timeout'])
                    #    logger.debug(f'new job. {t}')
                    except Exception:
                        logger.exception('failed to create new job')
        except:
            logger.exception(f'failed for {msg} :')

    def on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            logger.error(f'cannot connect to MQTT broker: {userdata} {flags} {rc}')
            return

        try:
            # control channels only
            self.subscribe(self.publish_to)
        except:
            logger.exception("subscription failed")
            self.client.on_disconnect()
        logger.info('mqtt connected!')
        self.is_connected = True

    def on_disconnect(self):
        self.disable()

    def publish(self, message):
        if not isinstance(message, tuple):
            print(f'bad message: {message}')
            return
        else:
            self.pub.put(message)

    def subscribe(self, channels):
        for channel in channels:
            r = self.client.subscribe(self.listen_to)
            if r[0] == 0:
                self.sub.append(channel)
            else:
                self.no_sub.append(channel)  # for later use
                logger.warning(f'failed to subscribe to {channel}')

    def disable(self):
        msg = 'MQTT server stop'
        self.is_connected = False
        self.disabled = True
        self.main.join(1)
        self.ping.join(1)
        self.no_sub = []
        self.sub = []
        print(msg)

    def _ping(self):
        print('start pinging')
        while True:
            if self.disabled:
                break
            for channel in self.config.dev_types:
                with PacketSender() as p:
                    packet = p.create('PING',
                                      dev_type=channel)
                    self.pub.put(packet.encode())
                time.sleep(self.config.timeout.get('basic', 1))


mqtt_send_queue = Queue()
server = MQTTServer(config=config,
                    queue=mqtt_send_queue)
