import logging

from core import models
from device import serializers

logger = logging.getLogger('skaben.main')


DEVICES = {
    'lock': {
        'serializer': serializers.LockSerializer,
        'model': models.Lock
    },
    'term': {
        'serializer': serializers.TerminalSerializer,
        'model': models.Terminal
    },
    'terminal': {
        'serializer': serializers.TerminalSerializer,
        'model': models.Terminal
    },
    'rgb': {
        'serializer': serializers.SimpleLightSerializer,
        'model': models.SimpleLight
    }
}


def save_devices(name, payload, queryset):
    device = DEVICES.get(name)
    if not device:
        raise Exception(f"{device} not found")
    try:
        for instance in queryset:
            serializer = device['serializer'](instance,
                                              data=payload,
                                              partial=True)
            if serializer.is_valid(): serializer.save()
    except Exception:
        logger.exception("exception occured")

