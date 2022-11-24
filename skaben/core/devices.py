from functools import lru_cache
from collections import namedtuple

import device.models as models
import device.serializers as schema


class DeviceConfig:

    devices: list
    device = namedtuple('Device', [
        'name',
        'type',
        'topic',
        'model',
        'schema'
    ])

    def __init__(self):
        # type, name, topic, model, schema
        self.devices = [
            self.device('simple', 'power', 'pwr', models.Simple, None),
            self.device('simple', 'light', 'rgb', models.Simple, None),
            self.device('simple', 'scale', 'scl', models.Simple, None),
            self.device('simple', 'box', 'box', models.Simple, None),
            self.device('smart', 'lock', 'lock', models.Lock, schema.LockSerializer),
            self.device('smart', 'terminal', 'terminal', models.Terminal, schema.TerminalSerializer)
        ]

    def topics(self, _type: str | None) -> [str]:
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
