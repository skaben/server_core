from datetime import datetime
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.timezone import now


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
        default=now
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

    is_ingame.fget.short_description = 'Внутриигровой статус'

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

    def __str__(self):
        s = f'[{self.order}] State: {self.name} ({self.info})'
        if self.current:
            return '===ACTIVE===' + s + '===ACTIVE==='
        else:
            return s


def get_current_alert_state() -> int:
    state = AlertState.objects.filter(current=True).first()
    return state.order if state else 0


def get_last_counter() -> int:
    counter = 0
    try:
        counter = AlertCounter.objects.latest('id').value
    except Exception:
        pass
    return counter


def get_current() -> AlertState:
    return AlertState.objects.filter(current=True).first()


def get_max_alert_value() -> int:
    states = [state.threshold for state in AlertState.objects.all().order_by("threshold")]
    return max(states) if states else 1


def get_borders() -> list:
    borders = [1, 500, 1000]
    return borders


def get_ingame_states() -> list:
    _range = (1, get_max_alert_value())
    return [state for state in AlertState.objects.all().order_by("threshold") if state.threshold in range(*_range)]


def new_alert_threshold_lg_current(level_name):
    current = get_current()
    try:
        new = AlertState.objects.filter(name=level_name).first()
        if new.threshold > current.threshold:
            return True
    except Exception as e:
        raise Exception(f"Error when comparing alert levels: alert level with name {level_name}\nreason: {e}")
