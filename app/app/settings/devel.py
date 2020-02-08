from .base import *

STATIC_ROOT = "/static/"

APP_ENV = 'dev'

ALLOWED_HOSTS = ['*']

#CORS_ORIGIN_ALLOW_ALL = True
#CORS_ALLOW_CREDENTIALS = False
#CORS_ORIGIN_WHITELIST = ['http://127.0.0.1:8089']

LOGGING['loggers'].update({
        'app': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'formatter': 'simple',
            'propagate': False
        }
})


APPCFG = {
    'timeout': 1,  # between pings
    'alive': 60,  #  set device offline after
    'text_storage': 'misc/texts', # texts directory
    'tz': 'Europe/Moscow', # timezone
    'debug': True,
    'mqtt': {
        'host': 'mosquitto',
        'port': 1883
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
        'aux_1',
        'gas'
    ]
}
