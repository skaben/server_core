import netaddr
from alert.models import AlertState
from core.helpers import format_routing_key, get_server_timestamp, get_hash_from
from core.transport.config import SkabenQueue
from core.transport.publish import get_interface
from django.conf import settings
from django.db import models


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
        return self.timestamp + settings.DEVICE_KEEPALIVE_TIMEOUT > get_server_timestamp()

    @property
    def alert(self) -> str:
        state = AlertState.objects.get_current()
        return str(getattr(state, "id", ""))

    @property
    def topic(self):
        return NotImplementedError

    @classmethod
    def _hash(cls, attrs: list[str]) -> str:
        return get_hash_from({attr: getattr(cls, attr) for attr in attrs})

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
