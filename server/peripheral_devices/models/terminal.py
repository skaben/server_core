from django.db import models
from peripheral_devices.models.base import SkabenDevice

__all__ = ("TerminalDevice",)


class TerminalDevice(SkabenDevice):
    """Smart terminal."""

    class Meta:
        verbose_name = "Терминал"
        verbose_name_plural = "Терминалы"

    powered = models.BooleanField(default=False, verbose_name="Питание подключено")
    blocked = models.BooleanField(default=False, verbose_name="Устройство заблокировано")
    account_set = models.ManyToManyField("peripheral_behavior.TerminalAccount")

    def get_hash(self) -> str:
        watch_list = ["alert", "powered", "blocked"]
        return super().hash_from_attrs(watch_list)
