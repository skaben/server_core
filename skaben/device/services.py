from core import models
from device import serializers
from transport.interfaces import send_log


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
            if serializer.is_valid():
                serializer.save()
    except Exception as e:
        send_log(f"exception occured when save device: {e}", "error")
