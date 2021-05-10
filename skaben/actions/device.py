from typing import Optional, List

import time

from device import serializers
from device.models import Lock, Simple, Terminal
from shape.models import SimpleConfig
from django.conf import settings
from transport.interfaces import publish_without_producer, send_log
from transport.rabbitmq import exchanges
from alert.models import get_current_alert_state


DEVICES = {
    'lock': {
        'serializer': serializers.LockSerializer,
        'model': Lock
    },
    'terminal': {
        'serializer': serializers.TerminalMQTTSerializer,
        'model': Terminal
    },
}

DEVICES['term'] = DEVICES['terminal']


def send_config_to_simple(simple_list: Optional[List[str]] = None):
    """Отправляем конфиг простым устройствам в соответствии с текущим уровнем тревоги"""
    if not simple_list:
        simple_list = [dev for dev in settings.APPCFG.get('device_types') if dev not in DEVICES]
    for device in simple_list:
        instance = SimpleConfig.objects.filter(dev_type=device, state__id=get_current_alert_state()).first()
        if not instance or not instance.config:
            continue
        rk = f'{device}.all.cup'
        payload = {
            'timestamp': int(time.time()),
            'datahold': instance.config
        }
        try:
            publish_without_producer(body=payload,
                                     exchange=exchanges.get('mqtt'),
                                     routing_key=rk)
        except Exception as e:
            send_log(f'{e}', 'ERROR')


def send_config_all(include_overrided: Optional[bool] = False):
    """Отправляем конфиг УМНЫМ устройствам"""
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
