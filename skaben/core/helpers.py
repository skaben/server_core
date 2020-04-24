import time
import pytz
from datetime import datetime

from django.conf import settings


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


class DeviceMixin:
    """
        Device online/offline status checker

        Todos:
            naming
    """
    ts = 0

    @property
    def offline(self):
        duration = int(time.time()) - \
                   (self.ts + settings.APPCFG.get('alive', 60))
        if duration > 0:
            return duration
        else:
            return 0


def timestamp_expired(timestamp):
    """ Check if timestamp is older than keepalive timeout """
    keep_alive = int(time.time()) - settings.APPCFG.get('alive', 60)
    return timestamp <= keep_alive


def update_timestamp(device_type, device_uid, timestamp=None):
   """ Checks if device is smart and updates timestamp """
   smart = settings.APPCFG.get('smart_devices')
   timestamp = timestamp if timestamp else int(time.time())
   if device_type in smart:
       try:
           model_class = getattr(smart.get(device_type), models)
           model_class.objects.get(uid=device_uid)
           device.ts = timestamp
           device.save()
       except Exception:
           # todo: error handling
           print(f'cannot update timestamp for {device_type} {device_uid}')
           pass

