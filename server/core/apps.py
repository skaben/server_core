from core.transport.config import get_mq_config
from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "core"

    def ready(self):
        """do something on app start"""
        get_mq_config()
