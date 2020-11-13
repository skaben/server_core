from django.db import models
from . import storages
from django.conf import settings


class File(models.Model):

    class Meta:
        abstract = True

    name = models.CharField(max_length=128, default="filename")

    @property
    def uri(self):
        return ''.join((settings.BASE_URL, self.file.path))

    def __str__(self):
        return f"<FILE {self.file.path}>"


class AudioFile(File):

    class Meta:
        verbose_name = 'файл: аудио'
        verbose_name_plural = "файлы: аудио"

    file = models.FileField(storage=storages.audio_storage)


class VideoFile(File):

    class Meta:
        verbose_name = 'файл: видео'
        verbose_name_plural = "файлы: видео"

    file = models.FileField(storage=storages.video_storage)


class ImageFile(File):

    class Meta:
        verbose_name = 'файл: изображения'
        verbose_name_plural = "файлы: изображений"

    file = models.ImageField(storage=storages.image_storage)


class TextFile(File):

    class Meta:
        verbose_name = 'файл: текст'
        verbose_name_plural = 'файлы: тексты'

    name = models.CharField(max_length=128, default="game doc")
    header = models.CharField(max_length=64, default="text document")
    content = models.TextField()