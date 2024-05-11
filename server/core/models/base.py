import re

from django.conf import settings
from polymorphic.models import PolymorphicModel
from core.helpers import get_uuid, get_server_timestamp
from core.validators import mac_validator
from django.db import models


class BaseModelPolymorphic(PolymorphicModel):
    class Meta:
        abstract = True

    uuid = models.UUIDField(primary_key=True, default=get_uuid, editable=False)


class BaseModelUUID(models.Model):
    """Model with UUID PK."""

    class Meta:
        abstract = True

    uuid = models.UUIDField(primary_key=True, default=get_uuid, editable=False)


class DeviceKeepalive(models.Model):
    """Device keepalive record keeper"""

    mac_addr = models.CharField(max_length=32, validators=[mac_validator])
    timestamp = models.PositiveIntegerField()

    def online(self):
        return self.timestamp + settings.DEVICE_KEEPALIVE_TIMEOUT > get_server_timestamp()

    def save(self, *args, **kwargs):
        self.mac_addr = re.sub(r"[^a-zA-Z0-9]", "", self.mac_addr)
        super().save(*args, **kwargs)
