import time
import multiprocessing as mp

from django.conf import settings


class Pinger(mp.Process):

    def __init__(self, connection, channel, exchange):
        self.producer = connection.Producer(channel)
        self.exchange = exchange
        self.topics = settings.APPCFG.get('device_types')
        timeout = settings.APPCFG.get('timeout', 1)
        self.timeout = round(timeout / len(self.topics), 1)
        super().__init__()

    def run(self):
        try:
            while True:
                current_time = int(time.time())
                for topic in self.topics:
                    self.producer.publish({"timestamp": current_time},
                                          exchange=self.exchange,
                                          routing_key=f'{topic}.all.PING')
                    time.sleep(self.timeout)
        except Exception:
            raise
