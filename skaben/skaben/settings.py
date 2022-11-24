"""
Django settings for SKABEN project
"""

import os
from django.core.management.utils import get_random_secret_key

# основные настройки проекта

ENVIRONMENT = os.environ.get("ENVIRONMENT", "")
DEBUG = False

if not ENVIRONMENT:
    raise ValueError('Environment not set!')

if not ENVIRONMENT.startswith("prod"):
    DEBUG = True

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = get_random_secret_key()

# urls

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', [])
DEFAULT_DOMAIN = os.environ.get('DEFAULT_DOMAIN', "http://127.0.0.1")
BASE_URL = os.environ.get('BASE_URL', 'http://127.0.0.1')
API_URL = os.environ.get('DJANGO_API_URL', 'http://127.0.0.1/api')

STATIC_URL = "static/"
STATIC_ROOT = "/static/"

MEDIA_URL = "media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "/media/")

ROOT_URLCONF = 'skaben.urls'

# CORS

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

# APPLICATIONS

INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'django_extensions',
    'alert',
    'actions',
    'assets',
    'core',
    'device',
    'eventlog',
    'shape',
    'skaben'
]

MIDDLEWARE = [
    'skaben.middleware.auth_middleware.AuthRequiredMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'skaben.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', 5432),
        'PASSWORD': os.environ.get('DB_PASS')
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# AUTHENTICATION

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# TIMEZONE + I18

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# CACHE

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache_table',
    }
}

# DRF

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
}

# LOGGING

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s :: <%(filename)s:%(lineno)s - '
                      '%(funcName)s()>  %(levelname)s > %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True
        },
    }
}

# RABBITMQ

RABBITMQ_USER = os.environ.get('RABBITMQ_USERNAME')
RABBITMQ_PASS = os.environ.get('RABBITMQ_PASSWORD')
AMQP_URI = f"pyamqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@rabbitmq:5672"
AMQP_TIMEOUT = 10
EXCHANGE_CHOICES = [
    ('mqtt', 'mqtt'),
    ('internal', 'internal')
]
MAX_CHANNEL_NAME_LEN = 64


if DEBUG:
    print('!! WARNING: RUNNING SKABEN IN DEBUG MODE !! API AUTHENTICATION DISABLED !!')
    ALLOWED_HOSTS = ['*']
    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': [],
        'DEFAULT_PERMISSION_CLASSES': [],
        'UNAUTHENTICATED_USER': None,
    }
    MEDIA_URL='media/'