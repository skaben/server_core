from core.devices import get_device_config
from core.transport.config import SkabenQueue
from core.transport.publish import get_interface
from core.helpers import format_routing_key


def handle(event_type: str, event_data: dict):
    devices = get_device_config()
    scale_topic = 'scl'
    
    if event_type == 'alert_state':
        # обновление конфигурации устройств при смене уровня тревоги
        for topic in devices.topics():
            with get_interface() as publisher:
                publisher.send_internal(
                    routing_key=format_routing_key(SkabenQueue.CLIENT_UPDATE.value, topic),
                    payload={},
                  )

    if event_type == 'alert_counter':
        with get_interface() as publisher:
            publisher.send_internal(
                routing_key=format_routing_key(SkabenQueue.CLIENT_UPDATE.value, scale_topic),
                payload={},
            )
