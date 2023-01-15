from django.db import models
from peripherals.models.devices import AbstractDevice

__all__ = 'Terminal'


class TerminalDevice(AbstractDevice):
    """Smart terminal."""

    class Meta:
        verbose_name = 'Терминал'
        verbose_name_plural = 'Терминалы'

    powered = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)
    hacked = models.BooleanField(default=False)
