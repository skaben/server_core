import time
from django.db import models

from core.helpers import get_time


class EventLog(models.Model):
    """
        Event log record
    """
    class Meta:
        verbose_name = 'База: Хроника событий'
        verbose_name_plural = 'База: Хроника событий'

    timestamp = models.IntegerField(default=int(time.time()))
    level = models.CharField(default="info", max_length=32)
    access = models.CharField(default="root", max_length=32)
    message = models.TextField()

    @property
    def human_time(self):
        return get_time(self.timestamp).split(' ')[1]

    def __str__(self):
        return f'{get_time(self.timestamp)}:{self.level}:{self.access} > {self.message}'


class UserInput(models.Model):

    name = models.CharField(default="inputname",
                            blank=False,
                            unique=True,
                            max_length=48)
    require = models.CharField(default="input", max_length=48)
    callback = models.CharField(default="callback", max_length=48)


class MQTTMessage(models.Model):
    """
        Message sent via MQTT
    """

    timestamp = models.IntegerField(default=int(time.time()))
    delivered = models.BooleanField(default=False)
    channel = models.CharField(max_length=16)
    topic = models.CharField(max_length=32)
    command = models.CharField(max_length=16)
    payload = models.TextField()
