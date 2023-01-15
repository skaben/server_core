from django.db import models
from peripherals.models.devices import AbstractDevice

__all__ = 'Passive'


class SimpleDevice(AbstractDevice):
    """Passive device, just listens, can not interact back."""

    class Meta:
        verbose_name = 'Пассивное устройство'
        verbose_name_plural = 'Пассивные устройства'

    channel = models.CharField(max_length=16)
