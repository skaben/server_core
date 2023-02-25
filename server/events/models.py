from core.helpers import get_time, get_uuid
from django.db import models


class EventRecord(models.Model):
    """Event log record"""
    class Meta:
        verbose_name = 'Игровое событие'
        verbose_name_plural = 'Игровые события'

    uuid = models.UUIDField(
        primary_key=True,
        editable=False,
        default=get_uuid
    )

    timestamp = models.IntegerField(default=0)
    level = models.CharField(default="info", max_length=32)
    stream = models.CharField(default="root", max_length=256)
    source = models.CharField(default="source", max_length=256)
    message = models.JSONField()

    @property
    def human_time(self):
        return get_time(self.timestamp).split(' ')[1]

    def __str__(self):
        message = "; ".join([f"{k}: {v}" for k, v in self.message.items()])
        return f'{get_time(self.timestamp)}:{self.level}:{self.stream} {self.source} > {message}'