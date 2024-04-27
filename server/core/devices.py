from collections import namedtuple
from functools import lru_cache
from typing import List

from django.conf import settings
from peripheral_devices import models
from peripheral_devices import serializers as schema

TOPIC = settings.SKABEN_DEVICE_TOPICS
FULL_DEVICE_LIST = [
    (*TOPIC.get("rgb"), None, None),
    (*TOPIC.get("pwr"), None, None),
    (*TOPIC.get("scl"), None, None),
    (*TOPIC.get("box"), None, None),
    (*TOPIC.get("lock"), models.LockDevice, schema.LockSerializer),
    (*TOPIC.get("terminal"), models.TerminalDevice, schema.TerminalSerializer),
]


class DeviceConfig:

    devices: list
    _named = namedtuple("Device", ["topic", "type", "model", "schema"])

    def __init__(self):
        # type, name, topic, model, schema
        self.devices = [self._named(*params) for params in FULL_DEVICE_LIST]

    @staticmethod
    def get_non_configured():
        return [settings.SKABEN_SCALE_TOPIC, "box"]

    def topics(self, _type: str | None = None) -> List[str]:
        if not _type:
            return [device.topic for device in self.devices]
        else:
            return [device.topic for device in self.devices if device.type == _type]

    def get_by_topic(self, topic):
        for device in self.devices:
            if device.topic == topic:
                return device


@lru_cache()
def get_device_config():
    return DeviceConfig()
