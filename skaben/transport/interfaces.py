import json
import time

from django.conf import settings
from transport.rabbitmq import exchanges, pool, connection


def send_plain(topic, data):
    with pool.acquire(block=True, timeout=10) as channel:
        prod = connection.Producer(channel)
        try:
            prod.publish(data,
                         exchange=exchanges.get('mqtt'),
                         routing_key=f"{topic}")
            res = f'success: {topic} with {data}'
        except Exception as e:
            res = dict(payload=f"FAILED: {topic} with {data} >> {e}",
                        exchange=exchanges.get('log'),
                        routing_key="error")
        finally:
            #channel.release()
            return res


def send_message(topic, uid, command, payload=None):
    data = {"timestamp": int(time.time())}
    if payload:
        data["datahold"] = payload
    send_plain(f"{topic}.{uid}.{command}", data)


def send_unicast_mqtt(topic, uid, command, payload=None):
    send_message(topic, uid, command, payload)


def send_broadcast_mqtt(topic, command, payload=None):
    send_message(topic, 'all', command, payload)
