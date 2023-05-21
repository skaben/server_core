from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from core.transport.publish import get_interface


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
    reason = models.CharField(
        verbose_name='Причина изменений',
        default='reason: changed by admin',
        max_length=64,
    )
    timestamp = models.DateTimeField(
        verbose_name='Время последнего изменения',
        default=timezone.now,
    )

    def save(self, *args, **kwargs):
        prev_alert_counter = AlertCounter.objects.order_by('-id').first()
        prev_value = 0 if not prev_alert_counter else prev_alert_counter.value

        super().save(*args, **kwargs)
        mq_interface = get_interface()
        mq_interface.send_event('alert_counter', {
            'counter': self.value,
            'increased': prev_value < self.value,
        })

    def __str__(self):
        return f'{self.value} {self.reason} at {self.timestamp}'


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
        verbose_name='порог срабатывания ',
        help_text=('Нижнее значение счетчика счетчика тревоги для переключения в статус. '
                   'Чтобы отключить авто-переключение - выставьте отрицательное значение'),
        default=-1
    )
    current = models.BooleanField(
        verbose_name='сейчас активен',
        default=False
    )
    order = models.IntegerField(
        verbose_name='цифровой id статуса',
        help_text='используется для идентификации и упорядочивания статуса без привязки к id в БД',
        blank=False,
        unique=True
    )
    modifier = models.IntegerField(
        verbose_name='штраф за ошибку',
        help_text='на сколько изменяется счетчик при ошибке прохождения данжа',
        default=5,
        blank=False
    )
    auto_increase = models.IntegerField(
        verbose_name='Авто-увеличение уровня тревоги',
        help_text='Увеличивается ли уровень со временем (settings.ALERT_COOLDOWN). Значение 0 выключает параметр',
        default=0,
    )
    auto_decrease = models.IntegerField(
        verbose_name='Применяется ли авто-сброс тревоги',
        help_text='Уменьшается ли уровень со временем (settings.ALERT_COOLDOWN). Значение 0 выключает параметр',
        default=0,
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

        if self.__original_state != self.current:
            mq_interface = get_interface()
            mq_interface.send_event('alert_state', {'state': self.name})
        self.__original_state = self.current

    is_final.fget.short_description = 'Финальный игровой статус'
    is_ingame.fget.short_description = 'Игровой статус'

    def __str__(self):
        s = f'[{self.order}] State: {self.name} ({self.info})'
        if self.current:
            return '===ACTIVE===' + s + '===ACTIVE==='
        else:
            return s
