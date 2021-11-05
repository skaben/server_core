import os
import sys
import time

from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        if 'runserver' in sys.argv:
            if os.environ.get('RUN_MAIN') == 'true':
                print('********** SKABEN SYSTEMS UP. SERVING THE OMNISSIAH **********')
