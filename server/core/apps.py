from django.apps import AppConfig
from core.transport.config import get_mq_config


class CoreConfig(AppConfig):
    name = "core"

    def ready(self):
        """do something on app start"""
        get_mq_config()
