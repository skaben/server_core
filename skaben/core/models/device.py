import time
from django.db import models
from django.conf import settings

from .menu import WorkMode
from .alert import AlertState


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
    ip = models.GenericIPAddressField()
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
        state = AlertState.objects.filter(current=True).first()
        _id = state.id if state else 0
        return str(_id)

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
        abstract = True
        verbose_name = 'Устройство пассивное'
        verbose_name_plural = 'Устройства пассивные'

    # todo:
    # timestamp = models.IntegerField(default=int(time.time()))
    # uid = models.CharField(max_length=16, unique=True)
    # info = models.CharField(max_length=256, default='simple dumb')
    # online = models.BooleanField(default=False)
    # ip = models.GenericIPAddressField()
    # subtype = models.CharField(max_length=32, default='rgb')
    # config = models.CharField(max_length=512, default='none')

    def __str__(self):
        return 'not implemented'
        #return f'DUMB ID: {self.id} {self.info}'


class SimpleLight(Simple):
    """
        Simple dumb device, such as lights, sirens, rgb-leds
        Controls only by predefined config in ConfigString
    """

    class Meta:
        verbose_name = 'Устройство RGB пассивное'
        verbose_name_plural = 'Устройства RGB пассивные'

    def __str__(self):
        return f'RGB light device {self.id} {self.info}'
