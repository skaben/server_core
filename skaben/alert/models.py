from datetime import datetime, timezone, timedelta
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.timezone import now


def get_current_timestamp() -> int:
    timestamp = now() - datetime(1970, 1, 1, tzinfo=timezone.utc) / timedelta(seconds=1)
    return timestamp


class AlertCounter(models.Model):

    """In-game Global Alert State counter"""

    class Meta:
        verbose_name = 'Тревога: счетчик уровня'
        verbose_name_plural = 'Тревога: счетчик уровня'

    value = models.IntegerField(
        verbose_name='Значение счетчика',
        help_text='Счетчик примет указанное значение, уровень тревоги может быть сброшен',
        default=0
    )
    comment = models.CharField(
        default='changed by admin',
        max_length=256
    )
    timestamp = models.DateTimeField(
        default=get_current_timestamp
    )

    def __str__(self):
        return f'{self.value} {self.comment} at {self.timestamp}'


class AlertState(models.Model):

    """In-game Global Alert State"""

    __original_state = None
    class Meta:
        verbose_name = 'Тревога: именной статус'
        verbose_name_plural = 'Тревога: именные статусы'

    name = models.CharField(
        verbose_name='название статуса',
        max_length=32,
        blank=False,
        unique=True
    )
    info = models.CharField(
        verbose_name='описание статуса',
        max_length=256
    )
    threshold = models.IntegerField(
        verbose_name='порог срабатывания',
        help_text=('Нижнее значение счетчика счетчика тревоги для переключения в статус. '
                   'Чтобы отключить авто-переключение - выставьте отрицательное значение'),
        default=-1
    )
    current = models.BooleanField(
        verbose_name='сейчас активен',
        default=False
    )
    order = models.IntegerField(
        verbose_name='цифровое обозначение статуса',
        blank=False,
        unique=True
    )
    modifier = models.IntegerField(
        verbose_name='модификатор счетчика',
        help_text='на сколько изменяется счетчик при ошибке прохождения данжа',
        default=5,
        blank=False
    )

    def __init__(self, *args, **kwargs):
        super(AlertState, self).__init__(*args, **kwargs)
        self.__original_state = self.current

    @property
    def is_ingame(self):
        """В игре ли статус"""
        return self.threshold >= 0

    @property
    def is_final(self):
        states = AlertState.objects.all().order_by('order')
        return states.last().id == self.id

    @property
    def get_current(self):
        if self.current:
            return self
        return AlertState.objects.all().filter(current=True).first()

    @staticmethod
    def get_by_name(name: str):
        return AlertState.objects.filter(name=name).first()

    def clean(self):
        has_current = AlertState.objects.all().exclude(pk=self.id).filter(current=True)
        if not self.current and not has_current:
            raise ValidationError('cannot unset current - no other current states')

    def save(self, *args, **kwargs):
        if self.current and not self.__original_state:
            other_states = AlertState.objects.all().exclude(pk=self.id)
            other_states.update(current=False)

        super().save(*args, **kwargs)
        self.__original_state = self.current

    is_final.fget.short_description = 'Финальный игровой статус'
    is_ingame.fget.short_description = 'Игровой статус'

    def __str__(self):
        s = f'[{self.order}] State: {self.name} ({self.info})'
        if self.current:
            return '===ACTIVE===' + s + '===ACTIVE==='
        else:
            return s
