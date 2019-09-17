import time
import pytz
import json
from datetime import datetime
from django.db import models
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db.models.fields.related import ManyToManyField
from django.utils.encoding import force_text

from sk_iface.model_printable import PrintableModel

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

class Log(PrintableModel):

    class Meta:
        verbose_name = 'Хроника событий'
        verbose_name_plural = 'Хроника событий'

    timestamp = models.IntegerField(default=int(time.time()))
    message = models.CharField(default='log message', max_length=1500)

    @property
    def human_time(self):
        return get_time(self.timestamp).split(' ')[1]

    def __str__(self):
        return f'{get_time(self.timestamp)} :: {self.message}'


class Value(PrintableModel):

    """
        current base alert level integer value
    """

    class Meta:
        verbose_name = 'Тревога: изменение уровня'
        verbose_name_plural = 'Тревога: изменения уровня'

    value = models.IntegerField(default=0)
    comment = models.CharField(default='changed by admin', max_length=250)
    timestamp = models.IntegerField(default=int(time.time()))

    def __str__(self):
        # TODO: move tz converter to helpers
        return f'{self.value} {self.comment} at {get_time(self.timestamp)}'


class State(PrintableModel):

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
        verbose_name = 'Тревога: статус'
        verbose_name_plural = 'Тревога: статусы'

    name = models.CharField(max_length=30)  # alert level color name
    descr = models.CharField(max_length=300)
    bg_color = models.CharField(max_length=7, default='#000000')
    fg_color = models.CharField(max_length=7, default='#ffffff')
    threshold = models.IntegerField(default=-1)
    current = models.BooleanField(default=False)

    def __str__(self):
        s = f'State: {self.name} ({self.descr})'
        if self.current:
            return '===ACTIVE===' + s + '===ACTIVE==='
        else:
            return s

class DevConfig(PrintableModel):

    """
        Configurations for different devices
    """

    class Meta:
        verbose_name = 'Конфиг: неуправляемые ус-ва'

    dev_subtype = models.CharField(max_length=50)
    state_name = models.CharField(max_length=30)
    config = models.CharField(max_length=300)

    def __str__(self):
        return f'{self.dev_subtype.upper()}-{self.state_name}'


class MenuItem(PrintableModel):

    class Meta:
        verbose_name = 'Игровой пункт меню'
        verbose_name_plural = 'Игровые пункты меню'

    descr = models.CharField(max_length=120)
    action = models.CharField(max_length=16)
    callback = models.CharField(max_length=16, blank=True)

#    @property
#    def menu_type(self):
#        normal = False
#        hacked = False
#        if self.id in self.menu_hacked.values_list('id', flat=True):
#            hacked = True
#        if self.id in self.menu_normal.values_list('id', flat=True):
#            normal = True
#        return {'normal': normal, 'hacked': hacked}

    @property
    def uid(self):
        return self.id

    def __str__(self):
        return f'[{self.action}] {self.descr} <{self.callback}>'


class Text(PrintableModel):

    image = 'img'
    text = 'text'

    type_choices = (
        (image, 'image file name'),
        (text, 'plain text'),
    )

    class Meta:
        verbose_name = 'Игровой документ'
        verbose_name_plural = 'Игровые документы'

    header = models.CharField(max_length=50)
    content = models.TextField()  # image name for images
    doctype = models.CharField(max_length=50,
                               choices=type_choices,
                               default=text)
    # lock timer for specific texts
    timer = models.IntegerField(default=0, blank=True)
    # if storing in filesystem
    #content = models.FileField(storage=FileSystemStorage(
    #    location=settings.APPCFG['text_storage']))

    @property
    def title(self):
        # backward compat.
        return self.header

    @property
    def uid(self):
        return self.id

    def __str__(self):
        s = f'<{self.doctype}> {self.header}'
        if self.timer:
           s = f'[TIMER: {self.timer}] ' + s
        return s

#  PERMISSIONS

class Card(PrintableModel):

    class Meta:
        verbose_name = 'Игровой код доступа'
        verbose_name_plural = 'Игровые коды доступа'

    code = models.CharField(max_length=8)
    name = models.CharField(max_length=30)
    surname = models.CharField(max_length=30)
    position = models.CharField(max_length=30)

    def __str__(self):
        return f'<{self.code}> {self.position} {self.surname}'


#  DEVICES

class Dumb(PrintableModel, DeviceMixin):
    """
        Simple dumb device, such as lights, sirens, rgb-leds
        Controls only by predefined config JSON
    """

    class Meta:
        verbose_name = 'Устройство (пасс.): RGB '
        verbose_name_plural = 'Устройства (пасс.): RGB'

    ts = models.IntegerField(default=int(time.time()))
    uid = models.CharField(max_length=16, unique=True)
    descr = models.CharField(max_length=120, default='simple dumb')
    online = models.BooleanField(default=False)
    ip = models.GenericIPAddressField()
    dev_subtype = models.CharField(max_length=50, default='rgb')
#    config = models.CharField(max_length=150, default='')

    def __str__(self):
        return f'DUMB ID: {self.id} {self.descr}'


class Lock(PrintableModel, DeviceMixin):

    class Meta:
        verbose_name = 'Устройство (акт.): Замок'
        verbose_name_plural = 'Устройства (акт.): Замки'

    ts = models.IntegerField(default=int(time.time()))
    uid = models.CharField(max_length=16, unique=True)
    descr = models.CharField(max_length=120, default='simple lock')
    online = models.BooleanField(default=False)
    ip = models.GenericIPAddressField()
    override = models.BooleanField(default=False)
    sound = models.BooleanField(default=False)
    opened = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)
    timer = models.IntegerField(default=10)

    @property
    def card_list(self):
        # unload list of Card codes for lock end-device
        acl = []
        state = State.objects.filter(current=True).first()
        for permission in self.permission_set.filter(state_id=state):
            acl.append(permission.card)
        return [card.code for card in acl]

    def __str__(self):
        return f'<{self.id}> {self.descr}'


class Terminal(PrintableModel, DeviceMixin):

    easy = 6
    normal = 8
    medium = 10
    hard = 12

    difficulty_choices = (
        (easy, 'easy'),
        (normal, 'normal'),
        (medium, 'medium'),
        (hard, 'hard'),
    )

    hack = 'hack'
    alert = 'alert'
    text = 'text'

    menu_choices = (
        (hack, 'hack access'),
        (alert, 'lower alert'),
        (text, 'read texts'),
    )


    class Meta:
        verbose_name = 'Устройство (акт.): Терминал'
        verbose_name_plural = 'Устройства (акт.): Терминалы'

    ts = models.IntegerField(default=int(time.time()))
    uid = models.CharField(max_length=16, unique=True)
    descr = models.CharField(max_length=120, default='simple terminal')
    online = models.BooleanField(default=False)
    ip = models.GenericIPAddressField()
    override = models.BooleanField(default=False)
    powered = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)
    block_time = models.IntegerField(default=10)
    hacked = models.BooleanField(default=False)
    hack_attempts = models.IntegerField(default=3)
    hack_difficulty = models.IntegerField(
                                choices=difficulty_choices,
                                default=easy)
    hack_wordcount = models.IntegerField(default=15)
    hack_chance = models.IntegerField(default=10)
    menu_normal = models.ManyToManyField(MenuItem, related_name='menu_normal')
    menu_hacked = models.ManyToManyField(MenuItem, related_name='menu_hacked')
    msg_header = models.CharField(max_length=100, default='terminal SK-100')
    status_header = models.CharField(max_length=100, default='', blank=True)
    msg_body = models.ManyToManyField(Text,
                                      null=True,
                                      blank=True,
                                      default=None)

#    lock_id = models.ForeignKey(Lock,
#                                null=True,
#                                blank=True,
#                                default=None,
#                                on_delete=models.CASCADE)

    @property
    def menu_items(self):
        menu_items = []
        for item in self.menu_hacked.all():
            as_dict = item.to_dict()
            if as_dict.get('action') == 'hack':
                # cannot be hacked twice
                continue
            if item in self.menu_normal.all():
                as_dict.update({'normal': True, 'hacked': True })
            else:
                as_dict.update({'normal': False, 'hacked': True})
            menu_items.append(as_dict)
        for item in self.menu_normal.all():
            # rare scenario
            if item not in self.menu_hacked.all():
                as_dict = item.to_dict()
                as_dict.update({'normal': True, 'hacked': False})
            menu_items.append(as_dict)
        return menu_items            
            

    def __str__(self):
        return f'TERMINAL ID: {self.id} {self.descr}'


class Permission(PrintableModel):

    class Meta:
        unique_together = ('card', 'lock')
        verbose_name = 'Игровые права доступа карт'
        verbose_name_plural = 'Игровые права доступа карт'

    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    lock = models.ForeignKey(Lock, on_delete=models.CASCADE)
    state_id = models.ManyToManyField(State)
    
    def __str__(self):
        return f'[ {self.lock.descr.upper()} ] {self.card.position} ' \
               f'{self.card.surname} '

