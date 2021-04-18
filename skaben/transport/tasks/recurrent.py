import multiprocessing as mp
import time
import traceback

from django.conf import settings
from transport.interfaces import send_broadcast_mqtt, send_log


class Pinger(mp.Process):

    def __init__(self):
        self.topics = settings.APPCFG.get('device_types')
        timeout = settings.APPCFG.get('timeout', 1)
        self.timeout = round(timeout / len(self.topics), 1)
        super().__init__()

    def run(self):
        self.running = True
        while self.running:
            try:
                for topic in self.topics:
                    send_broadcast_mqtt(topic, 'PING')
                    time.sleep(self.timeout)
            except Exception:
                send_log(f"{self.__class__.__name__} while running {traceback.format_exc()}")
