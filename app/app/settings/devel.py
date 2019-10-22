from .base import *

STATIC_ROOT = "/static/"

ALLOWED_HOSTS.extend([
    '192.168.0.200',
    '127.0.0.1'
])

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
        #'host': '127.0.0.1',
        'host': '192.168.0.200',
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
