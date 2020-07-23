from django.apps import AppConfig
from core.tasks.main import run_workers


class CoreConfig(AppConfig):
    name = 'core'

run_workers()