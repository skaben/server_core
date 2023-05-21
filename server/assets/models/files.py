import time
import uuid

from assets import storages
from core.helpers import get_hash_from
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models


class SkabenFile(models.Model):
    file: None

    class Meta:
        abstract = True

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, default="filename")
    hash = models.CharField(max_length=64, default='')

    @property
    def uri(self):
        return f"{settings.API_URL}{self.file.path}"

    def save(self, *args, **kwargs):
        self.hash = get_hash_from(f'{round(time.time())}{self.uuid}')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self._meta.verbose_name} `{self.name}`"


class AudioFile(SkabenFile):

    class Meta:
        verbose_name = 'Аудио'

    file = models.FileField(storage=storages.audio_storage)


class VideoFile(SkabenFile):

    class Meta:
        verbose_name = 'Видео'

    file = models.FileField(storage=storages.video_storage)


class ImageFile(SkabenFile):

    class Meta:
        verbose_name = 'Изображение'

    file = models.ImageField(storage=storages.image_storage)


class TextFile(models.Model):

    class Meta:
        verbose_name = 'Текстовый файл'

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, default="game doc")
    hash = models.CharField(max_length=64, default='')
    header = models.CharField(max_length=64, default="text document")
    content = models.TextField()
    file = models.FileField(storage=storages.text_storage, null=True, blank=True)

    @property
    def uri(self):
        return f"{settings.API_URL}{self.file.path}"

    def save(self, *args, **kwargs):
        self.hash = get_hash_from(f'{round(time.time())}{self.uuid}')
        file = ContentFile(self.content)
        self.file.save(content=file, name=f'{self.uuid}_{self.name}.txt', save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self._meta.verbose_name} `{self.name}`"
