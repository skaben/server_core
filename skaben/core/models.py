import time

from django.conf import settings
from django.db import models

# from django.core.files.storage import FileSystemStorage
# from django.db.models.fields.related import ManyToManyField
# from django.utils.encoding import force_text

from core.helpers import get_time


class DeviceMixin:
    """
        Device online/offline status checker

        Todos:
            naming
    """
    ts = 0

    @property
    def online(self):
        current = int(time.time())
        alive = settings.APPCFG.get('alive', 60)
        return self.timestamp > current - alive


class EventLog(models.Model):
    """
        Event log record
    """
    class Meta:
        verbose_name = 'Хроника событий'
        verbose_name_plural = 'Хроника событий'

    timestamp = models.IntegerField(default=int(time.time()))
    level = models.CharField(default="info", max_length=32)
    access = models.CharField(default="root", max_length=32)
    message = models.TextField()

    @property
    def human_time(self):
        return get_time(self.timestamp).split(' ')[1]

    def __str__(self):
        return f'{get_time(self.timestamp)}:{self.level}:{self.access} > {self.message}'


class AlertCounter(models.Model):

    """
        In-game Global Alert State counter
    """

    class Meta:
        verbose_name = 'Тревога: изменение уровня'
        verbose_name_plural = 'Тревога: изменения уровня'

    value = models.IntegerField(default=0)
    comment = models.CharField(default='changed by admin', max_length=256)
    timestamp = models.IntegerField(default=int(time.time()))

    def __str__(self):
        # TODO: move tz converter to helpers
        return f'{self.value} {self.comment} at {get_time(self.timestamp)}'


class AlertState(models.Model):

    """
        In-game Global Alert State

    """

    class Meta:
        verbose_name = 'Тревога: статус'
        verbose_name_plural = 'Тревога: статусы'

    name = models.CharField(max_length=32)  # alert level color name
    info = models.CharField(max_length=256)
    bg_color = models.CharField(max_length=7, default='#000000')
    fg_color = models.CharField(max_length=7, default='#ffffff')
    threshold = models.IntegerField(default=-1)
    current = models.BooleanField(default=False)

    def __str__(self):
        s = f'State: {self.name} ({self.info})'
        if self.current:
            return '===ACTIVE===' + s + '===ACTIVE==='
        else:
            return s


class ConfigString(models.Model):

    """
        Simple Device configuration string
    """

    class Meta:
        verbose_name = 'Конфиг: неуправляемые ус-ва'

    dev_subtype = models.CharField(max_length=64)
    state_name = models.CharField(max_length=32)
    config = models.CharField(max_length=256)

    def __str__(self):
        return f'{self.dev_subtype.upper()}-{self.state_name}'


class MenuItem(models.Model):
    ### TODO: режим доступа должен настраиваться отдельно для каждого терминала. не должно быть общего
    """
        In-game Terminal menu item
    """
    class Meta:
        verbose_name = 'Игровой пункт меню'
        verbose_name_plural = 'Игровые пункты меню'

    label = models.CharField(max_length=128)
    action = models.CharField(max_length=16)
    response = models.CharField(max_length=16, blank=True)
    access = models.CharField(max_length=2, default='10')

    @property
    def uid(self):
        return self.id

    def __str__(self):
        return f'[{self.action}] {self.label} <{self.response}>'


class Document(models.Model):
    """
        In-game document

        Todos:
            separate image document
    """

    image = 'img'
    text = 'text'

    type_choices = (
        (image, 'image file name'),
        (text, 'plain text'),
    )

    class Meta:
        verbose_name = 'Игровой документ'
        verbose_name_plural = 'Игровые документы'

    header = models.CharField(max_length=64)
    content = models.TextField()  # image name for images
    doctype = models.CharField(max_length=64,
                               choices=type_choices,
                               default=text)
    # lock terminal after time
    timer = models.IntegerField(default=0, blank=True)

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


# MINIGAMES


class HackGame(models.Model):

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

    class Meta:
        verbose_name = 'Настройки мини-игры взлома'
        verbose_name_plural = 'Настройки мини-игр взлома'

    attempts = models.IntegerField(default=3)
    difficulty = models.IntegerField(
                                     choices=difficulty_choices,
                                     default=easy)
    wordcount = models.IntegerField(default=15)
    chance = models.IntegerField(default=10)


class AnotherGame(models.Model):
    class Meta:
        verbose_name = 'Настройки мини-игры'
        verbose_name_plural = 'Настройки мини-игр'

    attempts = models.IntegerField(default=3)
    wordcount = models.IntegerField(default=15)
    chance = models.IntegerField(default=10)


#  PERMISSIONS


class AccessCode(models.Model):
    """
        In-game access code or card id
    """

    class Meta:
        verbose_name = 'Игровой код доступа'
        verbose_name_plural = 'Игровые коды доступа'

    code = models.CharField(max_length=8)
    name = models.CharField(max_length=64)
    surname = models.CharField(max_length=64)
    position = models.CharField(max_length=128)

    def __str__(self):
        return f'<{self.code}> {self.position} {self.surname}'


#  DEVICES

class Simple(models.Model, DeviceMixin):
    """
        Simple dumb device, such as lights, sirens, rgb-leds
        Controls only by predefined config in ConfigString
    """

    class Meta:
        verbose_name = 'Устройство пассивное'
        verbose_name_plural = 'Устройства пассивные'

    timestamp = models.IntegerField(default=int(time.time()))
    uid = models.CharField(max_length=16, unique=True)
    info = models.CharField(max_length=256, default='simple dumb')
    online = models.BooleanField(default=False)
    ip = models.GenericIPAddressField()
    subtype = models.CharField(max_length=32, default='rgb')
    config = models.ManyToManyField(ConfigString,
                                    blank=False,
                                    default='noop')

    def __str__(self):
        return f'DUMB ID: {self.id} {self.info}'


class SimpleLight(models.Model, DeviceMixin):
    """
        Simple dumb device, such as lights, sirens, rgb-leds
        Controls only by predefined config in ConfigString
    """

    class Meta:
        verbose_name = 'Устройство RGB пассивное'
        verbose_name_plural = 'Устройства RGB пассивные'

    timestamp = models.IntegerField(default=int(time.time()))
    uid = models.CharField(max_length=16, unique=True)
    info = models.CharField(max_length=256, default='simple dumb')
    online = models.BooleanField(default=False)
    ip = models.GenericIPAddressField()
    config = models.CharField(max_length=256, default='')

    def __str__(self):
        return f'DUMB ID: {self.id} {self.info}'


class Lock(models.Model, DeviceMixin):
    """
        Lock device class
    """

    class Meta:
        verbose_name = 'Устройство (акт.): Замок'
        verbose_name_plural = 'Устройства (акт.): Замки'

    timestamp = models.IntegerField(default=int(time.time()))
    uid = models.CharField(max_length=16, unique=True)
    info = models.CharField(max_length=128, default='simple lock')
    ip = models.GenericIPAddressField()
    override = models.BooleanField(default=False)
    sound = models.BooleanField(default=False)
    closed = models.BooleanField(default=True)
    blocked = models.BooleanField(default=False)
    timer = models.IntegerField(default=10)

    @property
    def acl(self):
        # unload list of Card codes for lock end-device
        acl = list()
        state = AlertState.objects.filter(current=True).first()
        for permission in self.permission_set.filter(state_id=state):
            acl.append(permission.card)
        return [card.code for card in acl]

    @property
    def permissions(self):
        # unload list of Card codes for lock end-device
        acl = {}
        for perm in self.permission_set.filter(lock_id=self.id):
            state_list = [state.name for state in perm.state_id.all()]
            acl[f"{perm.card.position} {perm.card.name}"] = state_list
        return acl

    def __str__(self):
        return f'<{self.id}> {self.info}'


class Terminal(models.Model, DeviceMixin):
    """
        Terminal device class
    """

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

    timestamp = models.IntegerField(default=int(time.time()))
    uid = models.CharField(max_length=16, unique=True)
    info = models.CharField(max_length=128, default='simple terminal')
    ip = models.GenericIPAddressField()
    override = models.BooleanField(default=False)
    powered = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)
    block_time = models.IntegerField(default=10)
    hacked = models.BooleanField(default=False)
    menu_normal = models.ManyToManyField(MenuItem, related_name='menu_normal')
    menu_hacked = models.ManyToManyField(MenuItem, related_name='menu_hacked')
    dev_header = models.CharField(max_length=128, default='terminal SK-100')
    status_header = models.CharField(max_length=128, default='', blank=True)
    mini_game = models.ManyToManyField(HackGame)
    document = models.ManyToManyField(Document,
                                      blank=True,
                                      default=None)

    @property
    def menu_items(self):
        # TODO: menu items set mode 10, 01, 11 for hacked/normal/both
        menu_items = []
        hacked = self.menu_hacked.all()
        normal = self.menu_normal.all()

        for item in hacked:
            as_dict = item.to_dict()
            if as_dict.get('action') == 'hack':
                # cannot be hacked twice
                continue
            if item in normal:
                as_dict.update({"access": "11"})
            else:
                as_dict.update({"access": "01"})
            menu_items.append(as_dict)
        for item in normal:
            # rare scenario
            if item not in hacked:
                as_dict = item.to_dict()
                as_dict.update({"access": "10"})
            menu_items.append(as_dict)
        return menu_items

    def __str__(self):
        return f'TERMINAL ID: {self.id} {self.info}'


class Permission(models.Model):
    """
        Access codes permission to open locks
    """

    class Meta:
        unique_together = ('card', 'lock')
        verbose_name = 'Игровые права доступа карт'
        verbose_name_plural = 'Игровые права доступа карт'

    card = models.ForeignKey(AccessCode, on_delete=models.CASCADE)
    lock = models.ForeignKey(Lock, on_delete=models.CASCADE)
    state_id = models.ManyToManyField(AlertState)

    def __str__(self):
        return f'[ {self.lock.info.upper()} ] {self.card.position} ' \
               f'{self.card.surname} '


class MQTTMessage(models.Model):
    """
        Message sent via MQTT
    """

    timestamp = models.IntegerField(default=int(time.time()))
    delivered = models.BooleanField(default=False)
    channel = models.CharField(max_length=16)
    topic = models.CharField(max_length=32)
    command = models.CharField(max_length=16)
    payload = models.TextField()
