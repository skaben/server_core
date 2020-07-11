import time
import pytz
from datetime import datetime

from django.conf import settings

from rest_framework.request import Request
from rest_framework.test import APIRequestFactory


def get_time(timestamp):
    """
        Converts unix timestamp to local time

        Todos:
            move to helpers
    """
    utc_time = datetime.utcfromtimestamp(timestamp)
    local = pytz.utc.localize(utc_time, is_dst=None) \
        .astimezone(pytz.timezone(settings.APPCFG['tz'])) \
        .strftime('%Y-%m-%d %H:%M:%S')
    return local


def timestamp_expired(timestamp):
    """ Check if timestamp is older than keepalive timeout """
    keep_alive = int(time.time()) - int(settings.APPCFG.get('alive', 60))
    return timestamp <= keep_alive


def hex_to_rgb(hex):
    """ converts hex to hsl """
    if hex.startswith('#'):
        hex = hex[1:]
    hex = ''.join([h.lower() for h in hex])
    return ",".join([str(i) for i in bytes.fromhex(hex)])


factory = APIRequestFactory()
request = factory.get('/')

dummy_context = {
    'request': Request(request),
}
