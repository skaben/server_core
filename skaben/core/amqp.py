from kombu import Connection
from kombu import Exchange, Queue, Consumer
from kombu.mixins import ConsumerMixin

import threading
import time

from django.conf import settings

connection = Connection(settings.AMQP_URL)
pool = connection.ChannelPool(64)

# creating exchanges
event_exchange = Exchange('internal', type='direct')
mqtt_exchange = Exchange('mqtt', type='topic')

# declaring exchanges
channel = pool.acquire()
for exchange in (event_exchange, mqtt_exchange):
    bound_exchange = exchange(channel)
    bound_exchange.declare()

channel.release()


class AskWorker(ConsumerMixin):
    """ Working with ASK Queue """

    def __init__(self, connection):
        self.connection = connection

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=task_queue,
                         accept=['json', 'pickle'],
                         callbacks=[self.task]
                         )]

    def task(self, body, message):
        print(body)
        listttt.append(body)
        message.ack()


try:
    worker = Worker(connection)
    worker.run()
except:
    pass

def kombu_prod(payload='test'):
    channel = pool.acquire()
    try:
        producer = connection.Producer(channel)

        producer.publish(
            'PING',
            retry=True,
            exchange='amq.fanout',
            routing_key='result',
            payload=payload
        )
        return 'done'
    except Exception:
        raise
    finally:
        channel.release()

listttt = []

# TODO: send config from client, display in real time in django

def kombu_cons():

    def get_message(body, message=None):
        if message:
            print('------------ RECEIVED MESSAGE: {0!r}'.format(body))
        else:
            print('111')

    #channel = pool.acquire()

    ask_queue = Queue('ask',
                       exchange=bound_exchange,
                       routing_key='ask.#',
                       durable=True,
                       )

    class Worker(ConsumerMixin):

        def __init__(self, connection):
            self.connection = connection

        def get_consumers(self, Consumer, channel):
            return [Consumer(queues=ask_queue,
                             accept=['json', 'pickle'],
                             callbacks=[self.task]
                             )]

        def task(self, body, message):
            dev_type, uid, command = message.delivery_info.get('routing_key').split('.')[1:]
            listttt.append(f"{dev_type}, {uid}, {command}")
            message.ack()

    try:
        worker = Worker(connection)
        worker.run()

    except Exception:
        raise

def drain():
    return listttt
    #try:
    #    connection.drain_events(timeout=.1)
    #except:
    #    pass
