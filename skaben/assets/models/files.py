import hashlib
import uuid

from assets import storages
from core.helpers import simple_hash
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models


class SkabenFile(models.Model):

    class Meta:
        abstract = True

    name = models.CharField(max_length=128, default="filename")
    hash = models.CharField(max_length=64, default='')

    @property
    def uri(self):
        return f"{settings.DEFAULT_DOMAIN}{self.file.path}"

    def save(self, *args, **kwargs):
        self.hash = simple_hash(f'{self.name}{uuid.uuid4()}')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self._meta.verbose_name} `{self.name}`"


class AudioFile(SkabenFile):

    class Meta:
        verbose_name = 'файл: аудио'
        verbose_name_plural = "файлы: аудио"

    file = models.FileField(storage=storages.audio_storage)


class VideoFile(SkabenFile):

    class Meta:
        verbose_name = 'файл: видео'
        verbose_name_plural = "файлы: видео"

    file = models.FileField(storage=storages.video_storage)


class ImageFile(SkabenFile):

    class Meta:
        verbose_name = 'файл: изображения'
        verbose_name_plural = "файлы: изображений"

    file = models.ImageField(storage=storages.image_storage)


class TextFile(models.Model):

    class Meta:
        verbose_name = 'Текстовый файл'
        verbose_name_plural = 'файлы: тексты'

    name = models.CharField(max_length=128, default="game doc")
    hash = models.CharField(max_length=64, default='')
    header = models.CharField(max_length=64, default="text document")
    content = models.TextField()
    file = models.FileField(storage=storages.text_storage, null=True, blank=True)

    @property
    def uri(self):
        return f"{settings.DEFAULT_DOMAIN}{self.file.path}"

    def save(self, *args, **kwargs):
        self.hash = simple_hash(f'txt{self.name}')
        file = ContentFile(self.content)
        self.file.save(content=file, name=f'{self.hash}_{self.name}.txt', save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self._meta.verbose_name} `{self.name}`"
