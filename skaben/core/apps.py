import os
import sys

from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        print('ready')
        # from server_core.skaben.core.transport.main import run_pinger, run_workers
        # if 'runserver' in sys.argv:
        #     if os.environ.get('RUN_MAIN') == 'true':
        #         print('starting workers')
        #         run_workers()
        #         print('starting pinger')
        #         print('********** SKABEN SYSTEMS UP. SERVING THE OMNISSIAH **********')
        #         run_pinger()
