import json
import uuid as _uuid
import base64
import hashlib
import time
from datetime import datetime
from random import sample
from string import ascii_lowercase

import pytz
from django import db
from django.conf import settings


def get_server_time() -> int:
    return int(time.time())


def get_uuid():
    return _uuid.uuid4()


def from_json(json_data: str | dict = dict) -> dict:
    """Получение данных из json"""
    if isinstance(json_data, dict):
        return json_data
    return json.loads(json_data)


def get_task_id() -> str:
    """Генерирует task id"""
    random_string = ''.join(sample(ascii_lowercase, 5)) + str(get_server_time())
    hasher = hashlib.md5(bytes(random_string, encoding="utf-8"))
    return base64.urlsafe_b64encode(hasher.digest()).decode("utf-8")


def get_hash_from(data: list | dict | str) -> str:
    """Simple hashing function"""
    if isinstance(data, dict) or isinstance(data, list):
        dump = json.dumps(data).encode('utf-8')
    elif isinstance(data, str):
        dump = bytes(data)
    else:
        raise TypeError(f'{type(data)} not supported, provide `dict`, `list` or `str` instead')
    return hashlib.md5(dump).hexdigest()


def timestamp_expired(timestamp: int) -> bool:
    """ Check if timestamp is older than keepalive timeout """
    keep_alive = int(time.time()) - 60  # todo: get from system settings
    return timestamp <= keep_alive


def get_time(timestamp: int) -> str:
    """ Convert unix timestamp to local time """
    utc_time = datetime.utcfromtimestamp(timestamp)
    local = pytz.utc.localize(utc_time, is_dst=None) \
        .astimezone(pytz.timezone(settings.TIM)) \
        .strftime('%Y-%m-%d %H:%M:%S')
    return local


def hex_to_rgb(hexdata: str) -> str:
    """ Convert hex to hsl """
    if hexdata.startswith('#'):
        hexdata = hexdata[1:]
    hexdata = ''.join([h.lower() for h in hexdata])
    return ",".join([str(i) for i in bytes.fromhex(hexdata)])


def fix_database_conn(func):
    """ Django/Kombu annoying bug fix """
    def wrapper(*args, **kwargs):
        for conn in db.connections.all():
            conn.close_if_unusable_or_obsolete()
        return func(*args, **kwargs)
    return wrapper


class Hashable(object):

    @staticmethod
    def _hash(obj: object, attrs: list[str]) -> str:
        return get_hash_from({attr: getattr(obj, attr) for attr in attrs})
