from alert.models import AlertState
from django.conf import settings
from django.db import models
from core.helpers import get_server_time

__all__ = [
    'DeviceMixin',
    'AbstractDevice'
]


class DeviceMixin:
    """Device mixin for keepalive status checks."""
    timestamp = 0

    @property
    def online(self):
        return self.timestamp + settings.DEVICE_KEEPALIVE_TIMEOUT < get_server_time()

    @property
    def alert_current(self):
        return str(AlertState.get_current.order or '')


class AbstractDevice(models.Model, DeviceMixin):
    """Abstract device."""

    class Meta:
        abstract = True

    ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP-адрес'
    )
    mac_addr = models.CharField(max_length=16, unique=True)
    description = models.CharField(max_length=128, default='smart complex device')
    timestamp = models.IntegerField(default=get_server_time)
    override = models.BooleanField(default=False)
