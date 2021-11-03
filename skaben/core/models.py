from typing import Optional
from django.db import models

from core.helpers import get_uuid
from transport.rabbitmq import exchanges


def get_default_dict():
    return {}


MAX_CHANNEL_LEN = 64
SIMPLE = 'simple'
SMART = 'smart'


class DeviceChannel(models.Model):

    class Meta:
        verbose_name = 'MQTT устройство'
        verbose_name_plural = 'MQTT устройства'

    TYPE_CHOICES = (
        (SIMPLE, 'simple'),
        (SMART, 'smart')
    )

    channel = models.CharField(
        max_length=MAX_CHANNEL_LEN,
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


class SystemSettings(models.Model):

    ping_timeout = models.IntegerField(
        verbose_name='Задержка посыла PING в канал',
        default=10
    )
    keep_alive = models.IntegerField(
        verbose_name='Keep-alive',
        help_text='Интервал через который устройство будет считаться оффлайн',
        default=60
    )
    energy_slots = models.IntegerField(
        verbose_name='количество ед. распределения энергии',
        default=3
    )


def get_system_settings() -> SystemSettings:
    settings = SystemSettings.objects.latest('id')
    if not settings:
        raise ValueError('System settings not configured in DB')
    return settings


EXCHANGE_CHOICES = [(exchange, exchange) for exchange in exchanges.keys()
                    if exchange in ['mqtt', 'websocket', 'internal']]


class ControlCommand(models.Model):

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
        default=get_default_dict,
    )

    channel = models.ForeignKey(
        DeviceChannel,
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
        max_length=MAX_CHANNEL_LEN * 2,
        choices=EXCHANGE_CHOICES,
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


def get_device_channels(_type: Optional[str] = None):
    devices = DeviceChannel.objects.filter(type=_type).all() if _type else DeviceChannel.objects.all()
    return [device.channel for device in devices] if devices else []
