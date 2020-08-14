import time
import traceback
from transport.rabbitmq import exchanges, pool, connection


def publish_without_producer(body, exchange, routing_key, timeout=2):
    try:
        with pool.acquire(block=True, timeout=timeout) as channel:
            prod = connection.Producer(channel)
            prod.publish(body,
                         exchange=exchange,
                         routing_key=routing_key)
    except Exception:
        raise

        
def publish_with_producer(body, exchange, routing_key, producer):
    try:
        producer.publish(body,
                         exchange=exchange,
                         routing_key=routing_key,
                         retry=True)
    except Exception:
        raise


def publish_with_producer(body, exchange, routing_key, producer):
    try:
        producer.publish(body,
                         exchange=exchange,
                         routing_key=routing_key,
                         retry=True)
    except Exception:
        raise

        
def send_log(message, level="INFO", producer=None):
    try:
        if not isinstance(message, dict):
            message = {"message": message}

        # uppercase is a good association with logging level, but routing keys is lower
        accepted = [x.lower() for x in ["DEBUG", "INFO", "WARNING", "ERROR"]]
        level = level.lower()

        if level not in accepted:
            return send_log(f"{level} not in accepted log level list: {accepted}", "error")

        kwargs = {
            "body": message,
            "exchange": exchanges.get('log'),
            "routing_key": level
        }

        if not producer:
            publish_without_producer(**kwargs)
        else:
            kwargs["producer"] = producer
            publish_with_producer(**kwargs)

    except Exception:
        raise Exception(f"{traceback.format_exc()}")


def send_websocket(message, level="info", access="root", producer=None):
    try:
        kwargs = {
            "body": message,
            "exchange": exchanges.get("websocket"),
            "routing_key": f"ws.{access}.{level}"
        }
        if not producer:
            publish_without_producer(**kwargs)
        else:

            kwargs["producer"] = producer
            publish_with_producer(**kwargs)
    except Exception:
        raise Exception(f"{traceback.format_exc()}")


def send_mqtt(topic, message, producer=None):
    try:
        kwargs = {
            "body": message,
            "exchange": exchanges.get('mqtt'),
            "routing_key": f"{topic}"
        }
        if not producer:
            publish_without_producer(**kwargs)
        else:
            publish_with_producer(producer=producer, **kwargs)
    except Exception:
        raise Exception(f"{traceback.format_exc()}")


def send_message_over_mqtt(topic, uid, command, payload=None):
    data = {"timestamp": int(time.time())}
    if payload:
        data["datahold"] = payload
    send_mqtt(f"{topic}.{uid}.{command}", data)


def send_unicast_mqtt(topic, uid, command, payload=None):
    send_message_over_mqtt(topic, uid, command, payload)


def send_broadcast_mqtt(topic, command, payload=None):
    # FIXME: YAGNI
    send_message_over_mqtt(topic, 'all', command, payload)
