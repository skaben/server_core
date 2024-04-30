from core.models.base import BaseModelUUID
from django.contrib.contenttypes.models import ContentType
from django.db import models

__all__ = ("TerminalMenuItem",)


class TerminalMenuItem(BaseModelUUID):

    class Meta:
        verbose_name = "Пункт меню терминала"
        verbose_name_plural = "Пункты меню терминала"

    timer = models.SmallIntegerField(default=0)
    description = models.CharField(max_length=128)
