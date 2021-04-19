import time

from django.db import models
from core.helpers import get_time


class AlertCounter(models.Model):

    """In-game Global Alert State counter"""

    class Meta:
        verbose_name = 'База: Тревога: счетчик уровня'
        verbose_name_plural = 'База: Тревога: счетчик уровня'

    value = models.IntegerField(default=0)
    comment = models.CharField(default='changed by admin', max_length=256)
    timestamp = models.IntegerField(default=int(time.time()))

    def __str__(self):
        # TODO: move tz converter to helpers
        return f'{self.value} {self.comment} at {get_time(self.timestamp)}'


class AlertState(models.Model):

    """In-game Global Alert State"""

    __original_state = None
    class Meta:
        verbose_name = 'База: Тревога: именной статус'
        verbose_name_plural = 'База: Тревога: именные статусы'

    name = models.CharField(max_length=32, blank=False, unique=True)  # alert level color name
    info = models.CharField(max_length=256)
    bg_color = models.CharField(max_length=7, default='#000000')
    fg_color = models.CharField(max_length=7, default='#ffffff')
    threshold = models.IntegerField(default=-1)
    current = models.BooleanField(default=False)
    order = models.IntegerField(blank=False, unique=True)
    modifier = models.IntegerField(default=5, blank=False)

    def __init__(self, *args, **kwargs):
        super(AlertState, self).__init__(*args, **kwargs)
        self.__original_state = self.current

    @property
    def is_ingame(self):
        return self.threshold >= 0

    @property
    def is_final(self):
        states = AlertState.objects.all().order_by('order')
        return states.last().id == self.id

    def save(self, *args, **kwargs):
        if not self.__original_state:
            other_states = AlertState.objects.all().exclude(pk=self.id)
            other_states.update(current=False)
        super().save(*args, **kwargs)
        self.__original_state = True

    def __str__(self):
        s = f'[{self.order}] State: {self.name} ({self.info})'
        if self.current:
            return '===ACTIVE===' + s + '===ACTIVE==='
        else:
            return s


def get_current_alert_state() -> int:
    state = AlertState.objects.filter(current=True).first()
    return state.id if state else 0