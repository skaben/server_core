from django.db import models
from .alert import AlertState


class MenuItem(models.Model):

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
        verbose_name = 'Настройки: (Терминал) элемент меню'
        verbose_name_plural = 'Настройки: (Терминал) элементы меню'

    name = models.CharField(max_length=48, default="menu action")
    timer = models.IntegerField(default=-1)
    option = models.CharField(choices=TYPE_CHOICES,
                              default=USER,
                              max_length=32)
    game = models.ForeignKey("HackGame", on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey("UserInput", on_delete=models.CASCADE, blank=True, null=True)
    audio = models.ForeignKey("AudioFile", on_delete=models.CASCADE, blank=True, null=True)
    video = models.ForeignKey("VideoFile", on_delete=models.CASCADE, blank=True, null=True)
    text = models.ForeignKey("TextFile", on_delete=models.CASCADE, blank=True, null=True)
    image = models.ForeignKey("ImageFile", on_delete=models.CASCADE, blank=True, null=True)

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
        verbose_name = 'Настройки: (Терминал) режим работы меню'
        verbose_name_plural = 'Настройки: (Терминал) режим работы меню'

    name = models.CharField(max_length=48, default="terminal mode")
    state = models.ManyToManyField(AlertState, blank=True)
    main_header = models.CharField(max_length=48, default="terminal vt40k")
    menu_set = models.ManyToManyField(MenuItem)

    @property
    def has_files(self):
        files = {}
        for item in self.menu_set.all():
            related = getattr(item, item.option)
            files.update({related.hash: related.uri})
        return files

    def __str__(self):
        return f"Mode <{self.name}>"
