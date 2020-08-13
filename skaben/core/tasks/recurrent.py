import time
import multiprocessing as mp

from django.conf import settings
from transport.interfaces import send_broadcast_mqtt


class Pinger(mp.Process):

    def __init__(self):
        self.topics = settings.APPCFG.get('device_types')
        timeout = settings.APPCFG.get('timeout', 1)
        self.timeout = round(timeout / len(self.topics), 1)
        super().__init__()

    def run(self):
        try:
            while True:
                for topic in self.topics:
                    send_broadcast_mqtt(topic, 'PING')
                    #self.producer.publish({"timestamp": current_time},
                    #                      exchange=self.exchange,
                    #                      routing_key=f'{topic}.all.PING')
                    time.sleep(self.timeout)
        except Exception:
            raise
