import time

from django.db import models


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
