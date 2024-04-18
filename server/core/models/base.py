import re

from core.helpers import get_uuid
from django.db import models

__all__ = (
    'BaseModelUUID',
)


class BaseModelUUID(models.Model):
    """Model with UUID PK."""

    class Meta:
        abstract = True

    uuid = models.UUIDField(
        primary_key=True,
        default=get_uuid,
        editable=False
    )


class DeviceKeepalive(models.Model):
    """Device keepalive record keeper"""

    mac_addr = models.CharField(max_length=32)
    timestamp = models.PositiveIntegerField()
    previous = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        self.mac_addr = re.sub(r'[^a-zA-Z0-9]', '', self.mac_addr)
        super().save(*args, **kwargs)
