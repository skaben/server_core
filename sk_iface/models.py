import time
import pytz
from datetime import datetime
from django.db import models
from django.conf import settings


def get_time(timestamp):
    utc_time = datetime.utcfromtimestamp(timestamp)
    local = pytz.utc.localize(utc_time, is_dst=None) \
        .astimezone(pytz.timezone(settings.APPCFG['tz'])) \
        .strftime('%Y-%m-%d %H:%M:%S')
    return local


class DeviceMixin:

    ts = 0  # default value

    @property
    def offline(self):
        duration = int(time.time()) - \
                   (self.ts + settings.APPCFG.get('alive', 60))
        if duration > 0:
            return duration
        else:
            return 0

# Create your models here.

class Log(models.Model):

    timestamp = models.IntegerField(default=int(time.time()))
    message = models.CharField(default='log message', max_length=1500)

    @property
    def human_time(self):
        return get_time(self.timestamp).split(' ')[1]

    def __str__(self):
        return f'{get_time(self.timestamp)} :: {self.message}'


class Value(models.Model):

    """
        current base alert level integer value
    """

    value = models.IntegerField(default=0)
    comment = models.CharField(default='changed by admin', max_length=250)
    timestamp = models.IntegerField(default=int(time.time()))

    def __str__(self):
        # TODO: move tz converter to helpers
        return f'{self.value} {self.comment} at {get_time(self.timestamp)}'


class State(models.Model):

    """

        WHITE/BLACK states switched only by operator

        thresholds stored for all levels

        BLUE >
        (needed power source)
        CYAN >
        (reactor loaded)
        GREEN >

        YELLOW/RED ( thresholds applying only on these levels)

    """

    class Meta:
        verbose_name = 'Global Alert state'
        verbose_name_plural = 'Global Alert states'

    name = models.CharField(max_length=30)  # alert level color name
    descr = models.CharField(max_length=300)
    bg_color = models.CharField(max_length=7, default='#000000')
    fg_color = models.CharField(max_length=7, default='#ffffff')
    threshold = models.IntegerField(default=-1)
    current = models.BooleanField(default=False)

    def update(self, **kwargs):
        for k in kwargs:
            if k == 'current':
                self.current = kwargs[k]
        self.save()

    def __str__(self):
        s = f'State: {self.name} ({self.descr})'
        if self.current:
            return '===ACTIVE===' + s + '===ACTIVE==='
        else:
            return s

class DevConfig(models.Model):

    """
        Configurations for different devices
    """

    dev_type = models.CharField(max_length=50)
    state_name = models.CharField(max_length=30)
    config = models.CharField(max_length=300)


#  DEVICES

class Dumb(models.Model, DeviceMixin):
    """
        Simple dumb device, such as lights, sirens, rgb-leds
        Controls only by predefined config JSON
    """

    class Meta:
        verbose_name = 'device: RGB (Dumb)'
        verbose_name_plural = 'devices: RGB (Dumbs)'

    ts = models.IntegerField(default=int(time.time()))
    descr = models.CharField(max_length=120, default='simple dumb')
    online = models.BooleanField(default=False)
    ip = models.GenericIPAddressField()
    dev_type = models.CharField(max_length=50, default='rgb')
    config = DevConfig.objects.filter(
        state_name=State.objects.filter(current=True),
        dev_type=dev_type)

    def __str__(self):
        return f'DUMB ID: {self.id} {self.descr}'


class Terminal(models.Model, DeviceMixin):

    class Meta:
        verbose_name = 'device: Terminal'
        verbose_name_plural = 'devices: Terminals'

    ts = models.IntegerField(default=int(time.time()))
    descr = models.CharField(max_length=120, default='simple terminal')
    online = models.BooleanField(default=False)
    ip = models.GenericIPAddressField()
    override = models.BooleanField(default=False)
    powered = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)
    hacked = models.BooleanField(default=False)
    opened = models.BooleanField(default=False) #
    lowered = models.BooleanField(default=False) #
    hack_attempts = models.IntegerField(default=3)
    hack_length = models.IntegerField(default=4)
    hack_wordcount = models.IntegerField(default=15)
    menu_list = models.CharField(max_length=12)
    msg_header = models.CharField(max_length=100)
    msg_body = models.CharField(max_length=500)
    base_state = State.objects.filter(current=True)

    @property
    def ishacked(self):
        if self.hacked:
            return True

    def __str__(self):
        return f'TERMINAL ID: {self.id} {self.descr}'


class Lock(models.Model, DeviceMixin):

    class Meta:
        verbose_name = 'device: Lock'
        verbose_name_plural = 'devices: Locks'

    ts = models.IntegerField(default=int(time.time()))
    # cardlist as 'color': 'cardid'
    descr = models.CharField(max_length=120, default='simple lock')
    online = models.BooleanField(default=False)
    ip = models.GenericIPAddressField()
    override = models.BooleanField(default=False)
    sound = models.BooleanField(default=False)
    opened = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)
    timer = models.IntegerField(default=10)
    term_id = models.ForeignKey(Terminal,
                                null=True,
                                blank=True,
                                default=None,
                                on_delete=models.CASCADE)
    base_state = State.objects.filter(current=True)

    @property
    def active(self):
        if self.ts + settings.APPCFG.get('alive', 60) >= int(time.time()):
            return True

    def __str__(self):
        return f'<{self.id}> {self.descr}'

#  PERMISSIONS

class Card(models.Model):

    class Meta:
        verbose_name = 'Staff card'
        verbose_name_plural = 'Staff cards'

    short_id = models.IntegerField()
    long_id = models.CharField(max_length=16, default='a8a7a6a5a4a3a2a1')
    name = models.CharField(max_length=30)
    surname = models.CharField(max_length=30)
    position = models.CharField(max_length=30)

    def __str__(self):
        return f'<{self.short_id}> {self.position} {self.surname}'


class Permission(models.Model):

    class Meta:
        unique_together = ['card_id', 'lock_id']
        verbose_name = 'Staff permission'
        verbose_name_plural = 'Staff permissions'

    card_id =  models.ForeignKey(Card, on_delete=models.CASCADE)
    lock_id = models.ForeignKey(Lock, on_delete=models.CASCADE)
    state_id = models.ManyToManyField(State)

    def __str__(self):
        return f'[ {self.lock_id.descr.upper()} ] {self.card_id.position} ' \
               f'{self.card_id.surname} ' \


# SIGNALS
