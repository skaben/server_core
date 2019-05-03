from django.apps import AppConfig


class IfaceConfig(AppConfig):
    name = 'sk_iface'

    def ready(self):
        from . import signals