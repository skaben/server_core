from django.db import models
from core.helpers import get_uuid

__all__ = 'BaseModelUUID'


class BaseModelUUID(models.Model):
    """Model with UUID PK."""

    class Meta:
        abstract = True

    uuid = models.UUIDField(
        primary_key=True,
        default=get_uuid,
        editable=False
    )
