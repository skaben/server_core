from .base import *

ALLOWED_HOSTS = ['*']

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = False
CORS_ORIGIN_WHITELIST = [
    'http://127.0.0.1:8080', 
    'http://127.0.0.1:15674',
    'http://192.168.0.254',
    'http://192.168.0.254:8080',
    'http://skaben',
    'http://skaben:8080',
    ]

LOGGING['loggers'].update({
        'skaben': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'formatter': 'simple',
            'propagate': False
        }
})


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [],
    'UNAUTHENTICATED_USER': None,
}


APPCFG = {
    'timeout': 1,  # between pings
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
        "ingame": 1,
        "max": 1000
    },
    'timeouts': {
        'device_keepalive': 15,
        'broker_keepalive': 10,
        'ping': 10
    },
    'device_types': [
        'terminal',
        'lock',
        'rgb',
        'pwr',
        'scl',
        'hold'
    ],
    'smart_devices': [
        'lock',
        'terminal'
    ],
    'additional_channels': [
        'aux_1',
        'gas'
    ],
}
