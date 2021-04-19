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
            rk = '{device_type}.{device_uid}.cup'.format(**payload)
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
