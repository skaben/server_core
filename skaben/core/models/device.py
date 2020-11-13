import time
from django.db import models
from django.conf import settings

from .config import LockConfig, TerminalConfig
from .menu import WorkMode


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

    timestamp = models.IntegerField(default=int(time.time()))
    uid = models.CharField(max_length=16, unique=True)
    info = models.CharField(max_length=128, default='smart complex device')
    ip = models.GenericIPAddressField()
    override = models.BooleanField(default=False)


class Lock(ComplexDevice):
    """
        Lock device class
    """

    class Meta:
        verbose_name = 'Устройство (акт.): Замок'
        verbose_name_plural = 'Устройства (акт.): Замки'

    config = models.ForeignKey(LockConfig, on_delete=models.CASCADE)

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
        verbose_name = 'Устройство (акт.): Терминал (консоль)'
        verbose_name_plural = 'Устройства (акт.): Терминалы (консоли)'

    config = models.ForeignKey(TerminalConfig, on_delete=models.CASCADE)
    modes_normal = models.ManyToManyField(WorkMode, related_name="mode_normal", blank=True, default=None)
    modes_extended = models.ManyToManyField(WorkMode, related_name="mode_extended", blank=True, default=None)

    @property
    def file_list(self):
        """get full unique file list for all modes"""
        result = []
        for qs in [self.modes_normal, self.modes_extended]:
            for mode in qs.all():
                result.extend([item.file.path for item in mode.has_files])
        return list(set(result))

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
