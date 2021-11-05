import logging
import multiprocessing as mp
import time
import traceback

from django.conf import settings
from transport.interfaces import send_log, send_message_over_mqtt


class Pinger(mp.Process):

    def __init__(self):
        self.topics = settings.APPCFG.get('device_types')
        self.timeout = settings.APPCFG.get('timeout', 1)
        super().__init__()

    def run(self):
        self.running = True
        while self.running:
            try:
                logging.info(f'pinging {self.topics}...')
                for topic in self.topics:
                    send_message_over_mqtt(topic, 'all', 'ping')
                    time.sleep(self.timeout)
            except Exception:
                send_log(f"{self.__class__.__name__} while running {traceback.format_exc()}")
