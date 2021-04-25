import time

from django.conf import settings
from django.db import models

from .alert import AlertState, get_current_alert_state
from .device_config import SimpleConfig, WorkMode


class DeviceMixin:
    """Device online/offline status checker"""
    ts = 0

    @property
    def online(self):
        current = int(time.time())
        alive = settings.APPCFG.get('alive', 60)
        return self.timestamp > current - alive


class ComplexDevice(models.Model, DeviceMixin):

    class Meta:
        abstract = True

    uid = models.CharField(max_length=16, unique=True)
    info = models.CharField(max_length=128, default='smart complex device')
    ip = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.IntegerField(default=int(time.time()))
    override = models.BooleanField(default=False)


class Lock(ComplexDevice):
    """
        Lock device class
    """

    class Meta:
        verbose_name = 'Клиент (устройство) Замок'
        verbose_name_plural = 'Клиент (устройство) Замки'

    sound = models.BooleanField(default=False)
    closed = models.BooleanField(default=True)
    blocked = models.BooleanField(default=False)
    timer = models.IntegerField(default=10)

    @property
    def acl(self):
        # unload list of Card codes for lock end-device
        acl = {}
        for perm in self.permission_set.filter(lock_id=self.id):
            state_list = [state.id for state in perm.state_id.all()]
            acl[f"{perm.card.code}"] = state_list
        return acl

    def __str__(self):
        return f'LOCK {self.ip} {self.info}'


class Terminal(ComplexDevice):

    """Smart terminal"""

    class Meta:
        verbose_name = 'Клиент (устройство) Терминал'
        verbose_name_plural = 'Клиент (устройство) Терминалы'

    powered = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)
    hacked = models.BooleanField(default=False)
    modes_normal = models.ManyToManyField(WorkMode, related_name="mode_normal", blank=True, default=None)
    modes_extended = models.ManyToManyField(WorkMode, related_name="mode_extended", blank=True, default=None)

    @property
    def mode_list(self):
        def get_mode_url(mode_queryset):
            return [mode.url for mode in mode_queryset.all()]

        return {
            "normal": get_mode_url(self.modes_normal),
            "extended": get_mode_url(self.modes_extended)
        }

    @property
    def alert(self):
        return str(get_current_alert_state())


    @property
    def file_list(self):
        """get full unique file list for all modes"""
        result = {}
        for qs in [self.modes_normal, self.modes_extended]:
            for mode in qs.all():
                result.update(**mode.has_files)
        return result

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
        state = get_current_alert_state()
        simple_config = SimpleConfig.objects.filter(
            dev_type=self.dev_type,
            state__id__lte=state
            ).order_by('state__order').all()
        if simple_config:
            return simple_config.last().config
        return {}

    def __str__(self):
        return f'device {self.dev_type} {self.uid} config: {self.config}'
