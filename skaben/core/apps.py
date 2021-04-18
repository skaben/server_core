import sys

from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        if 'runserver' in sys.argv:
            from transport.tasks.main import run_pinger, run_workers
            print('running workers')
            run_workers()
            run_pinger()
