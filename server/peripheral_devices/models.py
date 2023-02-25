import time

from alert.models import AlertState
from django.conf import settings
from django.db import models
# from .models import WorkMode, SimpleConfig


class DeviceMixin:
    """Device online/offline status checker."""
    timestamp = 0

    @property
    def online(self):
        current = int(time.time())
        alive = settings.DEVICE_KEEPALIVE_TIMEOUT
        return self.timestamp > current - alive

    @property
    def alert(self):
        return str(AlertState.get_current.order or '')


class ComplexDevice(models.Model, DeviceMixin):

    class Meta:
        abstract = True

    mac_addr = models.CharField(max_length=16, unique=True)
    info = models.CharField(max_length=128, default='smart complex device')
    ip = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.IntegerField(default=int(time.time()))
    override = models.BooleanField(default=False)


class Lock(ComplexDevice):
    """Lock device class."""

    class Meta:
        verbose_name = 'Лазерная дверь'
        verbose_name_plural = 'Лазерные двери'

    sound = models.BooleanField(default=False)
    closed = models.BooleanField(default=True)
    blocked = models.BooleanField(default=False)
    timer = models.IntegerField(default=10)

    @property
    def acl(self) -> dict:
        # unload list of Card codes for lock end-device
        acl = {}
        for perm in self.permission_set.filter(lock_id=self.id):
            state_list = [state.id for state in perm.state_id.all()]
            acl[f"{perm.card.code}"] = state_list
        return acl

    def __str__(self):
        return f'LOCK [ip: {self.ip}] {self.info}'


class Terminal(ComplexDevice):

    """Smart terminal"""

    class Meta:
        verbose_name = 'Терминал'
        verbose_name_plural = 'Терминалы'

    powered = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)
    hacked = models.BooleanField(default=False)
    modes_normal = models.ManyToManyField(WorkMode, related_name="mode_normal", blank=True, default=None)
    modes_extended = models.ManyToManyField(WorkMode, related_name="mode_extended", blank=True, default=None)

    def modes(self):
        for qs in [self.modes_normal, self.modes_extended]:
            for mode in qs.all():
                yield mode

    def __str__(self):
        return f"KONSOLE {self.ip} {self.info}"


class Simple(models.Model, DeviceMixin):
    """
        Simple dumb device, such as lights, sirens, rgb-leds
        Controls only by predefined config in ConfigString
    """

    class Meta:
        verbose_name = 'Клиент пассивный'
        verbose_name_plural = 'Клиенты пассивные'

    timestamp = models.IntegerField(default=int(time.time()))
    uid = models.CharField(max_length=16, unique=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    dev_type = models.CharField(max_length=16)

    @property
    def config(self):
        state = AlertState.get_current
        simple_config = SimpleConfig.objects.filter(
            dev_type=self.dev_type,
            state__id__lte=state
            ).order_by('state__order').all()
        if simple_config:
            return simple_config.last().config
        return {}

    def __str__(self):
        return f'device {self.dev_type} {self.uid} config: {self.config}'
