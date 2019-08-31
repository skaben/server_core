import os
import time
import pytest

from django.conf import settings
from django.core.management import call_command

@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        filepath = os.path.join(settings.BASE_DIR, 'test_data.json')
        call_command('loaddata', filepath)

#@pytest.fixture(scope='session', autouse=True)
#def django_db_setup():
#    settings.DATABASES['default'] = {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(settings.BASE_DIR, 'test_db.sqlite3'),
#    }

@pytest.fixture(scope='session', autouse=True)
def fake_message():

    def fake(dev_type='lock',
             uid='00ff00ff00ff',
             command='PONG',
             ts=int(time.time()),
             payload={'test':'data'}):
        return {'dev_type': dev_type,
                'ts': ts,
                'command': command,
                'payload': payload,
                'uid': uid}

    return fake
