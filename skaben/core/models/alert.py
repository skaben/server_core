import time
from django.db import models


class AlertCounter(models.Model):

    """In-game Global Alert State counter"""

    class Meta:
        verbose_name = 'Тревога: изменение уровня'
        verbose_name_plural = 'Тревога: изменения уровня'

    value = models.IntegerField(default=0)
    comment = models.CharField(default='changed by admin', max_length=256)
    timestamp = models.IntegerField(default=int(time.time()))

    def __str__(self):
        # TODO: move tz converter to helpers
        return f'{self.value} {self.comment} at {get_time(self.timestamp)}'


class AlertState(models.Model):

    """In-game Global Alert State"""

    class Meta:
        verbose_name = 'Тревога: статус'
        verbose_name_plural = 'Тревога: статусы'

    name = models.CharField(max_length=32)  # alert level color name
    info = models.CharField(max_length=256)
    bg_color = models.CharField(max_length=7, default='#000000')
    fg_color = models.CharField(max_length=7, default='#ffffff')
    threshold = models.IntegerField(default=-1)
    current = models.BooleanField(default=False)

    def __str__(self):
        s = f'State: {self.name} ({self.info})'
        if self.current:
            return '===ACTIVE===' + s + '===ACTIVE==='
        else:
            return s

