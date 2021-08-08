import os
import sys
import time

from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        if 'runserver' in sys.argv:
            if os.environ.get('RUN_MAIN') == 'true':
                from transport.tasks.main import run_pinger, run_workers
                print('starting workers')
                run_workers()
                print('starting pinger')
                print('********** SKABEN SYSTEMS UP. SERVING THE OMNISSIAH **********')
                run_pinger()
