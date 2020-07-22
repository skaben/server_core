import json
import time

from django.conf import settings
from transport.rabbitmq import exchanges, pool, connection


def send_plain(topic, data):
    with pool.acquire() as channel:
        prod = connection.Producer(channel)
        try:
            prod.publish(data,
                         exchange=exchanges.get('mqtt'),
                         routing_key=f"{topic}")
            return f'success: {topic} with {data}'
        except Exception as e:
            return dict(payload=f"FAILED: {topic} with {data} >> {e}",
                        exchange=exchanges.get('log'),
                        routing_key="error")


def send_message(topic, uid, command, payload={}):
    payload = json.loads(payload)
    data = {"timestamp": int(time.time()),
            "datahold": payload}
    send_plain(f"{topic}.{uid}.{command}", data)
