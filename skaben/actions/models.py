import time
from django.db import models


def get_current_timestamp():
    return int(time.time())


def get_dict():
    return {}


class EnergyState(models.Model):

    class Meta:
        verbose_name = 'Энергетический ресурс системы'
        verbose_name_plural = 'Энергетические ресурсы системы'

    timestamp = models.IntegerField(default=get_current_timestamp)
    slots = models.IntegerField(default=3)
    load = models.JSONField(default=get_dict, blank=True)

    def __str__(self):
        return f'[цикл {self.id}] энергетический ресурс системы: {self.slots}'
