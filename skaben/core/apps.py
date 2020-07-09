from django.apps import AppConfig
from tasks.scheduler import scheduler


class CoreConfig(AppConfig):
    name = 'core'


