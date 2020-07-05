import json

from kombu import Connection
from kombu import Exchange, Queue, Consumer
from kombu.mixins import ConsumerMixin, ConsumerProducerMixin

import threading
import multiprocessing as mp
import time

from django.conf import settings

from skabenproto import packets

from core.rabbit.workers import BaseWorker, AckNackWorker, \
    StateUpdateWorker, PingPongWorker, SendConfigWorker, LogWorker
from core.rabbit.recurrent import Pinger

connection = Connection(settings.AMQP_URL)
pool = connection.ChannelPool(64)

# exchanges

with pool.acquire() as channel:
    # main mqtt exchange, used mainly for messaging out.
    # note that all replies from clients starts with 'ask.' routing key goes to ask exchange
    mqtt_exchange = Exchange('mqtt', type='topic')
    bound_mqtt_exchange = mqtt_exchange(channel)

    # ask exchange collects all replies from client devices
    ask_exchange = Exchange('ask', type='topic')
    bound_ask_exchange = ask_exchange(channel)

    # logging exchange
    log_exchange = Exchange('log', type='direct')
    bound_log_exchange = log_exchange(channel)

    # note that is 'direct'-type
    # event_exchange serve as main internal server exchange, collecting all types of items
    events_exchange = Exchange('internal', type='direct')
    bound_events_exchange = events_exchange(channel)

    # declare exchanges
    for exchange in (bound_mqtt_exchange,
                     bound_events_exchange,
                     bound_ask_exchange,
                     bound_log_exchange):
        exchange.declare()
    # binding ask exchange to mqtt exchange with routing key
    bound_ask_exchange.bind_to(exchange=bound_mqtt_exchange,
                               routing_key='ask.#',
                               channel=channel)

# create and declare queues for MQTT exchange

# reply to pong
pong_queue = Queue('pong',
                   durable=False,
                   exchange=bound_ask_exchange,
                   routing_key='#.PONG')

# task delivery confirm
ack_queue = Queue('ack',
                  durable=False,
                  exchange=bound_ask_exchange,
                  routing_key='#.ACK')

nack_queue = Queue('nack',
                   durable=False,
                   exchange=bound_ask_exchange,
                   routing_key='#.NACK')

# queue for sending configs to client
cup_queue = Queue('cup',
                  durable=False,
                  exchange=bound_ask_exchange,
                  routing_key='#.CUP')

# server state updates
sup_queue = Queue('sup',
                  durable=False,
                  exchange=bound_ask_exchange,
                  routing_key='#.SUP')

info_queue = Queue('info',
                   durable=False,
                   exchange=bound_ask_exchange,
                   routing_key='#.INFO')

# declare queues for log exchange

log_queue = Queue("message",
                  durable=True,
                  exchange=bound_log_exchange,
                  routing_key="message")

error_queue = Queue("error",
                    durable=True,
                    exchange=bound_log_exchange,
                    routing_key="error")

# initiate workers

WORKERS = []
RECURRENT = {}


class WorkerProcess(mp.Process):

    def __init__(self, worker_class, connection, queues, exchanges, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.worker = worker_class(connection, queues, exchanges)

    def run(self):
        self.worker.run()


exchanges = {'ask': bound_ask_exchange,
             'internal': bound_events_exchange,
             'mqtt': bound_mqtt_exchange,
             'log': bound_log_exchange}


worker_processes = dict(
    worker_pong=WorkerProcess(worker_class=PingPongWorker,
                              connection=connection,
                              queues=[pong_queue, ],
                              exchanges=exchanges),

    worker_ack_nack=WorkerProcess(worker_class=AckNackWorker,
                                  connection=connection,
                                  queues=[ack_queue, nack_queue],
                                  exchanges=exchanges),

    worker_cup=WorkerProcess(worker_class=SendConfigWorker,
                             connection=connection,
                             queues=[cup_queue, ],
                             exchanges=exchanges),

    worker_sup_info=WorkerProcess(worker_class=StateUpdateWorker,
                                  connection=connection,
                                  queues=[sup_queue, info_queue],
                                  exchanges=exchanges),

    worker_messages=WorkerProcess(worker_class=LogWorker,
                                  connection=connection,
                                  queues=[log_queue, ],
                                  exchanges=exchanges)
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
                results.append(f"{name} already running")
        return results
    except Exception:
        raise


def run_pinger():
    _channel = pool.acquire()
    name = 'pinger'
    result = f'{name} already running'
    try:
        pinger = Pinger(name, connection, _channel, mqtt_exchange)
        if pinger.name not in RECURRENT:
            pinger.start()
            RECURRENT.update({name: pinger})
            result = f'{name} started'
        return result
    except Exception:
        raise

def send_plain(topic, data):
    with Connection(settings.AMQP_URL) as conn:
        with conn.channel() as channel:
            prod = conn.Producer(channel)
            try:
                prod.publish(data,
                             exchange=bound_mqtt_exchange,
                             routing_key=f"{topic}")
                return f'success: {topic} with {data}'
            except Exception as e:
                prod.publish(f"FAILED: {topic} with {data} >> {e}",
                             exchange=bound_log_exchange,
                             routing_key="error")

def send_message(topic, uid, command, payload={}):
    payload = json.loads(payload)
    data = {"timestamp": int(time.time()),
            "datahold": payload}
    send_plain(f"{topic}.{uid}.{command}", data)

def stop_all():
    try:
        results = []
        for name, proc in worker_processes.items():
            proc.kill()
            WORKERS.pop(WORKERS.index(name))
            results.append(f"terminated worker: {name}")
        names = []
        for name in RECURRENT:
            if RECURRENT.get(name):
                RECURRENT[name].kill()
                names.append(name)
                results.append(f"terminated recurrent task: {name}")
        [RECURRENT.pop(name) for name in names]
        return results
    except Exception:
        raise
