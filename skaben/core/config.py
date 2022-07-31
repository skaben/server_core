from enum import Enum
from functools import lru_cache

import device.models as models
import device.serializers as schema

__all__ = ['SimpleDeviceEnum', 'SmartDeviceEnum']


class SmartDeviceEnum(Enum):
    LOCK = {
        'topic': 'lock',
        'model': models.Lock,
        'schema': schema.LockSerializer
    }
    CONSOLE = {
        'topic': 'terminal',
        'model': models.Terminal,
        'schema': schema.TerminalSerializer
    }


class SimpleDeviceEnum(Enum):
    POWER = {
        'topic': 'pwr',
        'model': models.Simple,
        # 'schema': schema.PowerSerialize
    }
    LIGHT = {
        'topic': 'rgb',
        'model': models.Simple,
        # 'schema': schema.LightSchema
    }
    SCALE = {
        'topic': 'scl',
        'model': models.Simple,
        # 'schema': schema.ScaleSchema
    }


@property
@lru_cache
def topics_smart():
    """Возвращает список топиков сложных устройств"""
    return [e.value.get('topic') for e in SmartDeviceEnum]


@property
@lru_cache
def topics_simple():
    """Возвращает список топиков простых устройств"""
    return [e.value.get('topic') for e in SimpleDeviceEnum]


@property
def topics_full():
    """Возвращает полный список топиков"""
    return topics_simple() + topics_smart()