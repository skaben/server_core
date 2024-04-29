import netaddr
from alert.models import AlertState
from core.helpers import format_mac_address, format_routing_key, get_server_timestamp
from core.transport.config import SkabenQueue
from core.transport.publish import get_interface
from django.conf import settings
from django.db import models

__all__ = ("SkabenDevice",)


class SkabenDevice(models.Model):
    """Abstract device."""

    class Meta:
        abstract = True

    ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP-адрес")
    mac_addr = models.CharField(max_length=12, unique=True)
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

    def save(self, *args, **kwargs):
        """Сохранение, отправляющее конфиг устройству, если передан параметр send_update=True."""
        send_update = False

        if kwargs.get("send_update"):
            send_update = kwargs.pop("send_update")

        try:
            if len(self.mac_addr) < 12:
                raise ValueError
            self.mac_addr = str(netaddr.EUI(self.mac_addr, dialect=netaddr.mac_bare)).lower()
        except (netaddr.AddrFormatError, ValueError):
            raise ValueError(f"Invalid MAC address format: {self.mac_addr}")

        super().save(*args, **kwargs)

        if send_update:
            with get_interface() as publisher:
                publisher.publish(
                    body={},
                    exchange=publisher.config.exchanges.get("internal"),
                    routing_key=format_routing_key(SkabenQueue.CLIENT_UPDATE.value, self.mac_addr, "all"),
                )
