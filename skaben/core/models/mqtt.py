from core.helpers import get_uuid
from django.db import models
from django.conf import settings


__all__ =  [
    'DeviceTopic',
    'ControlReaction'
]

SIMPLE = 'simple'
SMART = 'smart'


class DeviceTopic(models.Model):

    class Meta:
        verbose_name = 'MQTT устройство'
        verbose_name_plural = 'MQTT устройства'

    TYPE_CHOICES = (
        (SIMPLE, 'simple'),
        (SMART, 'smart')
    )

    channel = models.CharField(
        max_length=settings.MAX_CHANNEL_NAME_LEN,
        unique=True,
        verbose_name='Канал MQTT'
    )

    type = models.CharField(
        max_length=16,
        choices=TYPE_CHOICES,
        default=SIMPLE,
        verbose_name="Тип устройства"
    )

    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name='Комментарий'
    )

    def __str__(self):
        return f'{self.channel} MQTT устройство [{self.type}]'


class ControlReaction(models.Model):
    """Управляющая команда"""

    uuid = models.UUIDField(
        primary_key=True,
        default=get_uuid,
        editable=False
    )

    name = models.CharField(
        verbose_name='Название команды',
        help_text='Должно быть уникальным',
        max_length=128,
        unique=True,
    )

    payload = models.JSONField(
        verbose_name='Полезная нагрузка',
        help_text='Указывайте просто dict',
        default=dict,
    )

    channel = models.ForeignKey(
        DeviceTopic,
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )

    comment = models.TextField(
        verbose_name='Комментарий',
        default='',
        blank=True
    )

    routing = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        verbose_name='Доп. параметры роутинга',
        help_text='Не трогайте это если не знаете что это'
    )

    exchange = models.CharField(
        max_length=settings.MAX_CHANNEL_NAME_LEN,
        choices=settings.EXCHANGE_CHOICES,
        default='mqtt',
        verbose_name='Выбор Exchange',
        help_text='Не трогайте это если не знаете что это'
    )


    @property
    def rk(self) -> str:
        """Actual routing key"""
        return f'{self.channel}.{self.routing}' if self.routing else self.channel

    def __str__(self):
        return f'Command {self.name} -> {self.comment[:64]}'

    class Meta:
        verbose_name = 'Управляющая команда'
