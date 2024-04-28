from alert.models import AlertState
from core.helpers import get_server_timestamp
from core.transport.publish import get_interface
from django.conf import settings
from django.db import models

__all__ = ("SkabenDevice",)


class SkabenDevice(models.Model):
    """Abstract device."""

    class Meta:
        abstract = True

    ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP-адрес")
    mac_addr = models.CharField(max_length=16, unique=True)
    description = models.CharField(max_length=128, default="smart complex device")
    timestamp = models.IntegerField(default=get_server_timestamp)
    override = models.BooleanField(default=False)
    
    @property
    def online(self) -> bool:
        return self.timestamp + settings.DEVICE_KEEPALIVE_TIMEOUT < get_server_timestamp()

    @property
    def alert_state(self) -> str:
        state = AlertState.get_current
        return str(getattr(state, "order", ""))

    @property
    def topic(self):
        return NotImplementedError
