import time

from core.helpers import get_time
from django.db import models


class EventLog(models.Model):
    """
        Event log record
    """
    class Meta:
        verbose_name = 'Игровое событие'
        verbose_name_plural = 'Игровые события'

    timestamp = models.IntegerField(default=int(time.time()))
    level = models.CharField(default="info", max_length=32)
    access = models.CharField(default="root", max_length=32)
    message = models.TextField()

    @property
    def human_time(self):
        return get_time(self.timestamp).split(' ')[1]

    def __str__(self):
        return f'{get_time(self.timestamp)}:{self.level}:{self.access} > {self.message}'
