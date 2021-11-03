from typing import Optional, List

import time

from device import serializers
from device.models import Lock, Simple, Terminal
from django.conf import settings
from transport.interfaces import publish_without_producer, send_log, send_ws_update
from transport.rabbitmq import exchanges


DEVICES = {
    'lock': {
        'serializer': serializers.LockSerializer,
        'model': Lock
    },
    'terminal': {
        'serializer': serializers.TerminalSerializer,
        'model': Terminal
    },
}

SIMPLE = [dev for dev in settings.APPCFG.get('device_types') if dev not in ['lock', 'terminal']]


def send_config_to_simple(simple_list: Optional[List[str]] = None):
    """Отправляем конфиг простым устройствам в соответствии с текущим уровнем тревоги"""
    if not simple_list:
        simple_list = SIMPLE

    # для каждого типа устройства генерится запрос во внутреннюю очередь
    for device in simple_list:
        rk = f'{device}.all.cup'
        dummy_body = {'device_type': device, 'device_uid': 'all'}
        publish_without_producer(body=dummy_body,
                                 exchange=exchanges.get('ask'),
                                 routing_key=rk)


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

    send_ws_update({
        'type': 'smart'
    })


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
    send_ws_update({
        'type': 'smart'
    })


def send_state_update(channel: str, packet: dict):
    pass


def update_terminals(payload: dict, uid: Optional[str] = None, include_overrided: bool = False):
    if not include_overrided:
        qs = Terminal.objects.filter(override=False).all()
    else:
        qs = Terminal.objects.all()
    if uid:
        qs = qs.filter(uid=uid)
    qs.update(**payload)


def update_locks(payload: dict, uid: Optional[str] = None, include_overrided: bool = False):
    if not include_overrided:
        qs = Lock.objects.filter(override=False).all()
    else:
        qs = Lock.objects.all()
    if uid:
        qs = qs.filter(uid=uid)
    qs.update(**payload)
