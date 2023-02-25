from django.db import models
from peripheral_devices.models.base import SkabenDevice

__all__ = (
    'SimpleDevice',
)


class SimpleDevice(SkabenDevice):
    """Passive device, just listens, can not interact back."""

    class Meta:
        verbose_name = 'Пассивное устройство'
        verbose_name_plural = 'Пассивные устройства'

    channel = models.CharField(max_length=16)
