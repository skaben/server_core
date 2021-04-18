from typing import Optional

from django.conf import settings

from core import models
from device import serializers
from transport.interfaces import publish_without_producer, send_log
from transport.rabbitmq import exchanges

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


def send_config_all(include_overrided: Optional[bool] = False):
    """Send config to all devices"""
    for dev in settings.APPCFG.get('device_types'):
        if not DEVICES.get(dev):
            continue

        for device in DEVICES[dev]['model'].objects.filter(override=include_overrided).all():
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



def send_config_to(channel: str):
    """Send existing config to channel"""
    dev = DEVICES.get(channel)
    if not dev:
        raise ValueError(f'unsupported device type {dev}')

    if dev.get('model'):
        for device in dev['model'].objects.filter(override=False).all():
            payload = {
                'device_type': dev,
                'device_uid': device.uid
            }
            rk = '{device_type}.{device_uid}.cup'.format(**payload)
            try:
                # emulate "config request" from client
                internal_exchange = exchanges.get('ask')
                publish_without_producer(body=payload,
                                         exchange=internal_exchange,
                                         routing_key=rk)
            except Exception as e:
                send_log(f'{e}', 'ERROR')


def send_state_update(channel: str, packet: dict):
    pass


# def update_smart_devices(device_type: str, payload: dict, queryset, no_send: bool = False):
#     """update all smart device configuration"""
#     device = DEVICES.get(device_type)
#     try:
#         if not device:
#             raise Exception(f"{device} not found")

#         for instance in queryset:
#             serializer = device['serializer'](instance,
#                                               data=payload,
#                                               partial=True,
#                                               context={"no_send": no_send})
#             if serializer.is_valid():
#                 return serializer.save()
#     except Exception as e:
#         send_log(f"exception occured when save device: {e}", "error")
