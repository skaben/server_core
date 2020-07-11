import json
import time

from kombu import Connection

from django.conf import settings
from transport.rabbitmq import exchanges


def send_plain(topic, data):
    with Connection(settings.AMQP_URL) as conn:
        with conn.channel() as channel:
            prod = conn.Producer(channel)
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
