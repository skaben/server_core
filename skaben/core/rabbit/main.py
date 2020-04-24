import json

from kombu import Connection
from kombu import Exchange, Queue, Consumer
from kombu.mixins import ConsumerMixin, ConsumerProducerMixin

import threading
import multiprocessing as mp
import time

from django.conf import settings

from skabenproto import packets
from core.rabbit.workers import AckNackWorker, StateUpdateWorker, PingPongWorker, SendConfigWorker

connection = Connection(settings.AMQP_URL)
pool = connection.ChannelPool(64)

WORKERS = []

# exchanges

# main mqtt exchange, used mainly for messaging out.
# note that all replies from clients starts with 'ask.' routing key goes to ask exchange
mqtt_exchange = Exchange('mqtt', type='topic')

# ask exchange collects all replies from client devices
ask_exchange = Exchange('ask', type='topic')

# note that is 'direct'-type
# event_exchange serve as main internal server exchange, collecting all types of items
events_exchange = Exchange('internal', type='direct')

# bound and declare exchanges

channel = pool.acquire()

bound_mqtt_exchange = mqtt_exchange(channel)
bound_ask_exchange = ask_exchange(channel)
bound_events_exchange = events_exchange(channel)

for exchange in (bound_mqtt_exchange, bound_ask_exchange, bound_events_exchange):
    exchange.declare()

# create and declare queues for MQTT exchange

# test ask queue
# ask_queue = Queue('ask',
#                    exchange=bound_mqtt_exchange,
#                    routing_key='ask.#',
#                    durable=True,
#                    )

# reply to pong
pong_queue = Queue('pong',
                   exchange=bound_ask_exchange,
                   routing_key='#.PONG')

# task delivery confirm
ack_queue = Queue('ack',
                  exchange=bound_ask_exchange,
                  routing_key='#.ACK')

nack_queue = Queue('nack',
                   exchange=bound_ask_exchange,
                   routing_key='#.NACK')

# queue for sending configs to client
cup_queue = Queue('cup',
                  exchange=bound_ask_exchange,
                  routing_key='#.CUP')

# server state updates
sup_queue = Queue('sup',
                  exchange=bound_ask_exchange,
                  routing_key='#.SUP')

info_queue = Queue('info',
                  exchange=bound_ask_exchange,
                  routing_key='#.INFO')

channel.release()

# initiate workers

class WorkerProcess(mp.Process):

    def __init__(self, worker_class, connection, queues, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.worker = worker_class(connection, queues)

    def run(self):
        self.worker.run()


worker_processes = dict(
    worker_pong=WorkerProcess(worker_class=PingPongWorker,
                              connection=connection,
                              queues=[pong_queue, ]),
    worker_ack_nack=WorkerProcess(worker_class=AckNackWorker,
                                  connection=connection,
                                  queues=[ack_queue, nack_queue]),
    worker_cup=WorkerProcess(worker_class=SendConfigWorker,
                             connection=connection,
                             queues=[cup_queue, ]),
    worker_sup_info=WorkerProcess(worker_class=StateUpdateWorker,
                                  connection=connection,
                                  queues=[sup_queue, info_queue]),
)


def run_workers():
    try:
        results = []
        for name, proc in worker_processes.items():
            if name not in WORKERS:
                proc.start()
                WORKERS.append(name)
                results.append(f"{name} start")
            else:
                results.append(f"{name} already started")
        return results
    except Exception:
        raise

# def kombu_prod(payload='test'):
#     channel = pool.acquire()
#     try:
#         producer = connection.Producer(channel)
#
#         producer.publish(
#             'PING',
#             retry=True,
#             exchange='mqtt',
#             routing_key='#'
#         )
#         return 'done'
#     except Exception:
#         raise
#     finally:
#         channel.release()
#
# listttt = []
#
# # TODO: send config from client, display in real time in django
#
# def kombu_cons():
#
#     def get_message(body, message=None):
#         if message:
#             print('------------ RECEIVED MESSAGE: {0!r}'.format(body))
#         else:
#             print('111')
#
#     # todo:
#
#     # PINGWorker
#     # ACK/NACK Worker
#     # CUP/SUP/INFO Worker
#
#     # todo:
#     # all workers inherits from base worker with check timestamp method
#     # with bad timestamp goes to CUP worker and updates
#     # exclusions managed inside Worker subclasses
#
#
# def drain():
#     return listttt
#     #try:
#     #    connection.drain_events(timeout=.1)
#     #except:
#     #    pass
