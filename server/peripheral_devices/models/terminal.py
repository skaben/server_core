from django.db import models
from peripheral_devices.models.base import SkabenDevice

__all__ = (
    'TerminalDevice',
)


class TerminalDevice(SkabenDevice):
    """Smart terminal."""

    class Meta:
        verbose_name = 'Терминал'
        verbose_name_plural = 'Терминалы'

    powered = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)
    hacked = models.BooleanField(default=False)
