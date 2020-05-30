import time
import multiprocessing as mp

from kombu import Producer
from django.conf import settings
from skabenproto.packets import PING


class Pinger(mp.Process):

    def __init__(self, name, connection, channel, exchange, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.producer = connection.Producer(channel)
        self.exchange = exchange

    def run(self):
        mqtt_topics = settings.APPCFG.get('device_types')
        timeout = settings.APPCFG.get('timeout', 1)
        try:
            while True:
                current_time = int(time.time())
                print(current_time)
                for topic in mqtt_topics:
                    self.producer.publish({"timestamp": current_time},
                                          exchange=self.exchange,
                                          routing_key=f'{topic}.all.PING')
                    #ping_packet = PING(topic=topic,
                    #                   timestamp=current_time)

                    #self.producer.publish(ping_packet.payload,
                    #                      exchange=self.exchange,
                    #                      routing_key=topic)

                time.sleep(timeout)
        except Exception:
            raise
