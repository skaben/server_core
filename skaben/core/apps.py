import sys
from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        if 'runserver' in sys.argv:
            from core.tasks.main import run_workers, run_pinger
            print('running workers')
            run_workers()
            run_pinger()
