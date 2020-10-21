import time
from . import storages

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


class UserInput(models.Model):

    name = models.CharField(default="inputname",
                            blank=False,
                            unique=True,
                            max_length=48)
    require = models.CharField(default="input", max_length=48)
    callback = models.CharField(default="callback", max_length=48)


class File(models.Model):

    class Meta:
        abstract = True

    name = models.CharField(max_length=128, default="filename")


class AudioFile(File):

    class Meta:
        verbose_name = 'файл аудио'
        verbose_name_plural = "файлы аудио"

    file = models.FileField(storage=storages.audio_storage)

    def __str__(self):
        return f"audio {self.name}"


class VideoFile(File):

    class Meta:
        verbose_name = 'файл видео'
        verbose_name_plural = "файлы видео"

    file = models.FileField(storage=storages.video_storage)

    def __str__(self):
        return f"video {self.name}"


class ImageFile(File):

    class Meta:
        verbose_name = 'файл изображения'
        verbose_name_plural = "файлы изображений"

    file = models.ImageField(storage=storages.image_storage)

    def __str__(self):
        return f"image {self.name}"


class TextDocument(models.Model):

    class Meta:
        verbose_name = 'текстовый документ'
        verbose_name_plural = 'текстовые документы'

    name = models.CharField(max_length=128, default="game doc")
    header = models.CharField(max_length=64, default="text document")
    content = models.TextField()


class MenuItem(models.Model):

    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    GAME = "game"
    USER = "user"

    TYPE_CHOICES = (
        (AUDIO, "audio"),
        (VIDEO, "video"),
        (IMAGE, "image"),
        (TEXT, "text"),
        (GAME, "game"),
        (USER, "input"),
    )

    name = models.CharField(max_length=48, default="menu action")
    timer = models.IntegerField(default=-1)
    option = models.CharField(choices=TYPE_CHOICES,
                              default=USER,
                              max_length=32)
    game = models.ForeignKey("HackGame", on_delete=models.CASCADE, blank=True, null=True)
    image_file = models.ForeignKey("ImageFile", on_delete=models.CASCADE, blank=True, null=True)
    text_file = models.ForeignKey("TextDocument", on_delete=models.CASCADE, blank=True, null=True)
    user_input = models.ForeignKey("UserInput", on_delete=models.CASCADE, blank=True, null=True)
    audio_file = models.ForeignKey("AudioFile", on_delete=models.CASCADE, blank=True, null=True)
    video_file = models.ForeignKey("VideoFile", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        timer = f"{self.timer}s" if self.timer > 0 else "not set"
        return f"Menu Item `{self.name}` ({self.option}) with timer: {timer}"


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
    difficulty = models.IntegerField(choices=difficulty_choices,
                                     default=normal)
    wordcount = models.IntegerField(default=15)
    chance = models.IntegerField(default=15)


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


# TERMINAL MODES (REGIMES)


class WorkMode(models.Model):
    """Terminal work regime"""

# todo:
#    default = "default"
#    extended = "extended"
#    terminal_themes = (
#        (default, 'default green'),
#        (extended, 'extended blue'),
#    )

    class Meta:
        verbose_name = 'Режим работы терминала'
        verbose_name_plural = 'Режимы работы терминала'

    name = models.CharField(max_length=48, default="terminal mode")
    state_id = models.ManyToManyField(AlertState, blank=True)
    main_header = models.CharField(max_length=48, default="terminal vt40k")
    menu_normal = models.ManyToManyField(MenuItem, related_name="menu_normal")
    menu_hacked = models.ManyToManyField(MenuItem, related_name="menu_hacked")

    @property
    def get_associated_files(self):
        for item in self.menu_hacked.all():
            print(item)

    def __str__(self):
        return f"[terminal regime {self.id}] "

# todo:
#    style_image = models.ForeignKey(ImageFile, on_delete=models.CASCADE)
#    style_theme = models.CharField(max_length=48)
#  DEVICES

#  TODO: abstract models

# DEVICES


class Simple(models.Model, DeviceMixin):
    """
        Simple dumb device, such as lights, sirens, rgb-leds
        Controls only by predefined config in ConfigString
    """

    class Meta:
        abstract = True
        verbose_name = 'Устройство пассивное'
        verbose_name_plural = 'Устройства пассивные'

    timestamp = models.IntegerField(default=int(time.time()))
    uid = models.CharField(max_length=16, unique=True)
    info = models.CharField(max_length=256, default='simple dumb')
    online = models.BooleanField(default=False)
    ip = models.GenericIPAddressField()
    subtype = models.CharField(max_length=32, default='rgb')
    config = models.CharField(max_length=512, default='none')
   # config = models.ManyToManyField(ConfigString,
   #                                 blank=False,
   #                                 default='noop')

    def __str__(self):
        return f'DUMB ID: {self.id} {self.info}'


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


class Complex(models.Model, DeviceMixin):

    class Meta:
        abstract = True

    timestamp = models.IntegerField(default=int(time.time()))
    uid = models.CharField(max_length=16, unique=True)
    info = models.CharField(max_length=128, default='smart complex device')
    ip = models.GenericIPAddressField()
    override = models.BooleanField(default=False)


class Lock(Complex):
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


class Terminal(Complex):

    """Smart terminal"""

    class Meta:
        verbose_name = 'Устройство (акт.): Терминал'
        verbose_name_plural = 'Устройства (акт.): Терминалы'

    powered = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)
    block_time = models.IntegerField(default=10)
    hacked = models.BooleanField(default=False)
    modes = models.ForeignKey(WorkMode, on_delete=models.CASCADE, blank=True, default=None)


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
