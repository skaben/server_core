from device import serializers
from transport.interfaces import publish_without_producer, send_log
from transport.rabbitmq import exchanges

from .models import Lock, Terminal

DEVICES = {
    'lock': {
        'serializer': serializers.LockSerializer,
        'model': models.Lock
    },
    'terminal': {
        'serializer': serializers.TerminalMQTTSerializer,
        'model': models.Terminal
    },
    # 'rgb': {
    #     'serializer': serializers.SimpleLightSerializer,
    #     'model': models.SimpleLight
    # }
}

DEVICES['term'] = DEVICES['terminal']


def send_config_all():
    for dev in ['terminal', 'lock']:
        for device in DEVICES[dev]['model'].objects.filter(override=False).all():
            payload = {
                'device_type': dev,
                'device_uid': device.uid
            }
            rk = '{device_type}.{device_uid}.CUP'.format(**payload)
            try:
                publish_without_producer(body=payload,
                                         exchange=exchanges.get('ask'),
                                         routing_key=rk)
            except Exception as e:
                send_log(f'{e}', 'ERROR')


def update_smart_devices(device_type: str, payload: dict, queryset, no_send: bool = False):
    """update all smart device configuration"""
    device = DEVICES.get(device_type)
    try:
        if not device:
            raise Exception(f"{device} not found")

        for instance in queryset:
            serializer = device['serializer'](instance,
                                              data=payload,
                                              partial=True,
                                              context={"no_send": no_send})
            if serializer.is_valid():
                return serializer.save()
    except Exception as e:
        send_log(f"exception occured when save device: {e}", "error")
