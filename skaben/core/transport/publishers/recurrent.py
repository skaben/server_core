import logging
import time

from django.conf import settings
from skabenproto import PING
from core.config import topics_full
from core.transport.interface import get_interface


def ping_devices():
    running = True
    message = f'[+] start pinger with interval {settings.AMQP_TIMEOUT} for topics: {", ".join(topics_full)}'
    logging.info(message)
    interface = get_interface()
    while running:
        for topic in topics_full:
            packet = PING(topic, timestamp=int(time.time()))
            interface.send_mqtt_skaben(packet)
        time.sleep(settings.AMQP_TIMEOUT)
