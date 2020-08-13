import time
import pytz
from random import randint
from datetime import datetime

from django import db
from django.conf import settings


def timestamp_expired(timestamp):
    """ Check if timestamp is older than keepalive timeout """
    keep_alive = int(time.time()) - int(settings.APPCFG.get('alive', 60))
    return timestamp <= keep_alive


def get_time(timestamp):
    """ Convert unix timestamp to local time """
    utc_time = datetime.utcfromtimestamp(timestamp)
    local = pytz.utc.localize(utc_time, is_dst=None) \
        .astimezone(pytz.timezone(settings.APPCFG['tz'])) \
        .strftime('%Y-%m-%d %H:%M:%S')
    return local


def hex_to_rgb(hex):
    """ Convert hex to hsl """
    if hex.startswith('#'):
        hex = hex[1:]
    hex = ''.join([h.lower() for h in hex])
    return ",".join([str(i) for i in bytes.fromhex(hex)])


def get_task_id(name='task'):
    """ generate task id """
    num = ''.join([str(randint(0, 9)) for _ in range(10)])
    return f"{name}-{num}"


def fix_database_conn(func):
    """ Django/Kombu annoying bug fix """
    def wrapper(*args, **kwargs):
        for conn in db.connections.all():
            conn.close_if_unusable_or_obsolete()
        return func(*args, **kwargs)
    return wrapper
