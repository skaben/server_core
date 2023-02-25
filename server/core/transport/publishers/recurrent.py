import logging
import time

from threading import Thread
from django.conf import settings
from skabenproto import PING
from core.devices import get_device_config


devices = get_device_config()


class Pinger(Thread):
    def __init__(self, *args, **kwargs):
        super(Pinger, self).__init__(*args, **kwargs)
        self.interface = None

    def run(self):
        topics = devices.topics()
        message = f'[+] start pinger with interval {settings.AMQP_TIMEOUT} for topics: {", ".join(topics)}'
        logging.info(message)
        while 1:
            for topic in topics:
                packet = PING(topic, timestamp=int(time.time()))
                self.interface.send_mqtt_skaben(packet)
            time.sleep(settings.AMQP_TIMEOUT)
