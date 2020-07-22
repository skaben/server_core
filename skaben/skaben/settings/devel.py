from .base import *

STATIC_ROOT = "/static/"

APP_ENV = 'dev'

ALLOWED_HOSTS = ['*']

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = False
#CORS_ORIGIN_WHITELIST = ['http://127.0.0.1:8089']

LOGGING['loggers'].update({
        'skaben': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'formatter': 'simple',
            'propagate': False
        }
})


APPCFG = {
    'timeout': 5,  # between pings
    'alive': 60,  #  set device offline after
    'text_storage': 'misc/texts', # texts directory
    'tz': 'Europe/Moscow', # timezone
    'debug': True,
    'mqtt': {
        'host': 'rabbitmq',
        'port': 1883
    },
    'alert': {
        "min": -5,
        "ingame": 0,
        "max": 1000
    },
    'timeouts': {
        'device_keepalive': 15,
        'broker_keepalive': 10,
        'ping': 1
    },
    'device_types': [
        'term',
        'lock',
        'rgb',
        'pwr',
    ],
    'additional_channels': [
        'aux_1',
        'gas'
    ],
}
