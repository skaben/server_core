import logging

from alert.service import AlertService
from core.transport.topics import get_topics
from django.conf import settings
from peripheral_behavior.models.passive import PassiveConfig


def get_passive_config(device_type: str) -> dict:
    config = {}
    topics = get_topics()
    with AlertService() as service:
        current = service.get_state_current()
        if not current:
            return config
        try:
            if device_type == topics.SCL:  # cоздаем конфиг для шкал
                counter = service.get_last_counter()
                config = {
                    "level": counter,
                    "state": current.name,
                    "borders": service.split_thresholds(count=3),
                }
            else:
                cfg = PassiveConfig.objects.get(topic=device_type, state=current)
                config = cfg.config
        except PassiveConfig.DoesNotExist:
            logging.error(f"device {device_type} config for state {current.name} not exists")
            pass
    return config
