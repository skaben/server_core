from core.helpers import get_uuid
from django.conf import settings
from django.db import models


def get_default_dict():
    return {}


class UserAction(models.Model):

    class Meta:
        abstract = True

    uuid = models.UUIDField(
        primary_key=True,
        editable=False,
        default=get_uuid
    )

    action = models.CharField(
        default='action',
        blank=False,
        unique=True,
        max_length=64,
        verbose_name='Уникальное имя операции'
    )

    display = models.CharField(
        blank=False,
        max_length=128,
        verbose_name='Отображаемое имя пункта меню'
    )


class UserInput(UserAction):

    expected = models.CharField(
        default="",
        max_length=128,
        blank=True,
        verbose_name='Ожидаемое значение ввода',
        help_text="Оставьте все поля пустыми чтобы сделать простую кнопку"
    )

    message = models.TextField(
        default="required input",
        verbose_name='Сообщение для пользователя на экране ввода'
    )

    delay = models.IntegerField(
        default=0,
        verbose_name='Задержка интерфейса пользователя'
    )

    class Meta:
        verbose_name = 'Пользовательский интерфейс ввода'
        verbose_name_plural = 'Пользовательские интерфейсы ввода'

    def __str__(self):
        return f"Input `{self.action}` required `{self.require}`"


class MenuItem(UserAction):

    # TODO: refactor choices include naming

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

    class Meta:
        verbose_name = 'Элемент меню терминала'
        verbose_name_plural = 'Элементы меню терминала'

    timer = models.IntegerField(default=-1)
    option = models.CharField(choices=TYPE_CHOICES,
                              default=USER,
                              max_length=32)
    game = models.ForeignKey("assets.HackGame", on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(UserInput, on_delete=models.CASCADE, blank=True, null=True)
    audio = models.ForeignKey("assets.AudioFile", on_delete=models.CASCADE, blank=True, null=True)
    video = models.ForeignKey("assets.VideoFile", on_delete=models.CASCADE, blank=True, null=True)
    text = models.ForeignKey("assets.TextFile", on_delete=models.CASCADE, blank=True, null=True)
    image = models.ForeignKey("assets.ImageFile", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        timer = f"{self.timer}s" if self.timer > 0 else "not set"
        return f"Menu Item `{self.name}` ({self.option}) with timer: {timer}"


class WorkMode(models.Model):
    """Terminal work regime"""

    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"

    class Meta:
        verbose_name = 'Режим (полное меню) терминала'
        verbose_name_plural = 'Режим (полное меню) терминала'

    uuid = models.UUIDField(primary_key=True, default=get_uuid, editable=False)
    name = models.CharField(max_length=48, default="terminal mode")
    state = models.ManyToManyField('alert.AlertState', blank=True)
    header = models.CharField(max_length=48, default="terminal vt40k")
    footer = models.CharField(max_length=48, default="unauthorized access is strictly prohibited")
    menu_set = models.ManyToManyField('shape.MenuItem')

    @property
    def url(self):
        # well, DRF needed request object for generate URL, but workers don't know about request at all
        return '/'.join((settings.API_URL, '/api/workmode', f"{self.id}"))

    @property
    def has_files(self):
        files = {}
        for item in self.menu_set.all():
            related = getattr(item, item.option)
            if hasattr(related, 'hash'):
                files.update({related.hash: related.uri})
        return files

    def __str__(self):
        return f"Mode <{self.name}>"


class AccessCode(models.Model):
    """In-game access code or card id"""

    class Meta:
        verbose_name = 'Код доступа (ключ-карта)'
        verbose_name_plural = 'Коды доступа (ключ-карты)'

    code = models.CharField(max_length=8)
    name = models.CharField(max_length=64)
    surname = models.CharField(max_length=64)
    position = models.CharField(max_length=128)

    def __str__(self):
        return f'<{self.code}> {self.position} {self.surname}'


class Permission(models.Model):
    """Access codes permission to open locks"""

    class Meta:
        unique_together = ('card', 'lock')
        verbose_name = 'Доступ ключ-карты (права)'
        verbose_name_plural = 'Доступы ключ-карт (права)'

    card = models.ForeignKey('shape.AccessCode', on_delete=models.CASCADE)
    lock = models.ForeignKey('device.Lock', on_delete=models.CASCADE)
    state_id = models.ManyToManyField('alert.AlertState')

    def __str__(self):
        return f'[ {self.lock.info.upper()} ] /{self.card.code}/ {self.card.position} ' \
               f'{self.card.surname} '


class SimpleConfig(models.Model):
    """
        Simple dumb device, such as lights, sirens, rgb-leds
    """

    class Meta:
        verbose_name = 'Поведение пассивного устройства'
        verbose_name_plural = 'Поведение пассивных устройств'

    # fixme: get_default_dict
    config = models.JSONField(default=get_default_dict)
    dev_type = models.CharField(max_length=16)
    state = models.ForeignKey('alert.AlertState',
                              on_delete=models.SET_NULL,
                              null=True,
                              blank=True)

    def __str__(self):
        name = 'UNDEFINED'
        if self.state:
            name = self.state.name.upper()
        return f'{self.dev_type} config [{name}] {self.config}'
