from core import models
from device import serializers
from transport.interfaces import send_log


DEVICES = {
    'lock': {
        'serializer': serializers.LockSerializer,
        'model': models.Lock
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

DEVICES['term'] = DEVICES['terminal']


def save_devices(device_type, payload, queryset, context={"send_config": True}):
    """ Save multiple devices configuration, updates will be sent by default """
    device = DEVICES.get(device_type)
    try:
        if not device:
            raise Exception(f"{device} not found")

        for instance in queryset:
            serializer = device['serializer'](instance,
                                              data=payload,
                                              partial=True,
                                              context=context)
            if serializer.is_valid():
                serializer.save()
    except Exception as e:
        send_log(f"exception occured when save device: {e}", "error")