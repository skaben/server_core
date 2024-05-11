# Generated by Django 5.0.3 on 2024-05-09 23:49

import assets.storages
import assets.validators.asset_validators
import core.helpers
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='audiofile',
            options={'verbose_name': 'Аудио файл', 'verbose_name_plural': 'Аудио файлы'},
        ),
        migrations.AlterModelOptions(
            name='imagefile',
            options={'verbose_name': 'Изображение', 'verbose_name_plural': 'Изображения'},
        ),
        migrations.AlterModelOptions(
            name='textfile',
            options={'verbose_name': 'Текстовый файл', 'verbose_name_plural': 'Текстовые файлы'},
        ),
        migrations.AlterModelOptions(
            name='videofile',
            options={'verbose_name': 'Видео файл', 'verbose_name_plural': 'Видео файлы'},
        ),
        migrations.RemoveField(
            model_name='audiofile',
            name='id',
        ),
        migrations.RemoveField(
            model_name='imagefile',
            name='id',
        ),
        migrations.RemoveField(
            model_name='textfile',
            name='header',
        ),
        migrations.RemoveField(
            model_name='textfile',
            name='id',
        ),
        migrations.RemoveField(
            model_name='userinput',
            name='message',
        ),
        migrations.RemoveField(
            model_name='videofile',
            name='id',
        ),
        migrations.AddField(
            model_name='textfile',
            name='ident',
            field=models.CharField(default='asd', help_text='Только латиница и цифры. Не будет виден игрокам.', max_length=128, unique=True, validators=[django.core.validators.RegexValidator(message='Only alphanumeric characters are allowed.', regex='^[a-zA-Z0-9]+$')], verbose_name='Идентификатор'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='audiofile',
            name='file',
            field=models.FileField(help_text='поддерживаются .ogg, .wav, .mp3 файлы', storage=assets.storages.OverwriteStorage(location='/media/audio'), upload_to='', validators=[assets.validators.asset_validators.audio_validator]),
        ),
        migrations.AlterField(
            model_name='audiofile',
            name='hash',
            field=models.CharField(default='', editable=False, max_length=64),
        ),
        migrations.AlterField(
            model_name='audiofile',
            name='name',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='audiofile',
            name='uuid',
            field=models.UUIDField(default=core.helpers.get_uuid, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='imagefile',
            name='file',
            field=models.ImageField(help_text='поддерживаются .png, .jpg, .webp файлы', storage=assets.storages.OverwriteStorage(location='/media/image'), upload_to='', validators=[assets.validators.asset_validators.image_validator]),
        ),
        migrations.AlterField(
            model_name='imagefile',
            name='hash',
            field=models.CharField(default='', editable=False, max_length=64),
        ),
        migrations.AlterField(
            model_name='imagefile',
            name='name',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='imagefile',
            name='uuid',
            field=models.UUIDField(default=core.helpers.get_uuid, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='textfile',
            name='content',
            field=models.TextField(help_text='Введенный текст будет сконвертирован в текстовый файл после сохранения.', verbose_name='Содержимое'),
        ),
        migrations.AlterField(
            model_name='textfile',
            name='hash',
            field=models.CharField(default='', editable=False, max_length=64),
        ),
        migrations.AlterField(
            model_name='textfile',
            name='name',
            field=models.CharField(help_text='Это название файла будет видно игрокам.', max_length=128, verbose_name='Название файла'),
        ),
        migrations.AlterField(
            model_name='textfile',
            name='uuid',
            field=models.UUIDField(default=core.helpers.get_uuid, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='userinput',
            name='action',
            field=models.CharField(default='action', help_text='Значение будет передано в составе INFO пакета `action: <значение>`', max_length=64, unique=True, verbose_name='Передаваемое значение'),
        ),
        migrations.AlterField(
            model_name='userinput',
            name='expected',
            field=models.CharField(blank=True, default='', help_text='По этому значению может быть выполнена проверка поля `user_input` INFO пакета', max_length=128, verbose_name='Ожидаемое значение'),
        ),
        migrations.AlterField(
            model_name='videofile',
            name='file',
            field=models.FileField(help_text='поддерживаются .webm, .mp4 файлы', storage=assets.storages.OverwriteStorage(location='/media/video'), upload_to='', validators=[assets.validators.asset_validators.video_validator]),
        ),
        migrations.AlterField(
            model_name='videofile',
            name='hash',
            field=models.CharField(default='', editable=False, max_length=64),
        ),
        migrations.AlterField(
            model_name='videofile',
            name='name',
            field=models.CharField(max_length=128),
        ),
        migrations.AlterField(
            model_name='videofile',
            name='uuid',
            field=models.UUIDField(default=core.helpers.get_uuid, editable=False, primary_key=True, serialize=False),
        ),
    ]
