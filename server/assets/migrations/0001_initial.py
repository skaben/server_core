# Generated by Django 4.1.7 on 2023-02-25 18:06

import assets.storages
import core.helpers
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AudioFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('name', models.CharField(default='filename', max_length=128)),
                ('hash', models.CharField(default='', max_length=64)),
                ('file', models.FileField(storage=assets.storages.OverwriteStorage(location='/media/audio'), upload_to='')),
            ],
            options={
                'verbose_name': 'Аудио',
            },
        ),
        migrations.CreateModel(
            name='HackGame',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attempts', models.IntegerField(default=3)),
                ('difficulty', models.IntegerField(choices=[(6, 'easy'), (8, 'normal'), (10, 'medium'), (12, 'hard')], default=8)),
                ('wordcount', models.IntegerField(default=15)),
                ('chance', models.IntegerField(default=15)),
            ],
            options={
                'verbose_name': 'Настройки мини-игры Fallout Hack',
            },
        ),
        migrations.CreateModel(
            name='ImageFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('name', models.CharField(default='filename', max_length=128)),
                ('hash', models.CharField(default='', max_length=64)),
                ('file', models.ImageField(storage=assets.storages.OverwriteStorage(location='/media/image'), upload_to='')),
            ],
            options={
                'verbose_name': 'Изображение',
            },
        ),
        migrations.CreateModel(
            name='TextFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('name', models.CharField(default='game doc', max_length=128)),
                ('hash', models.CharField(default='', max_length=64)),
                ('header', models.CharField(default='text document', max_length=64)),
                ('content', models.TextField()),
                ('file', models.FileField(blank=True, null=True, storage=assets.storages.OverwriteStorage(location='/media/text'), upload_to='')),
            ],
            options={
                'verbose_name': 'Текстовый файл',
            },
        ),
        migrations.CreateModel(
            name='UserInput',
            fields=[
                ('uuid', models.UUIDField(default=core.helpers.get_uuid, editable=False, primary_key=True, serialize=False)),
                ('action', models.CharField(default='action', max_length=64, unique=True, verbose_name='Уникальное имя операции')),
                ('expected', models.CharField(blank=True, default='', max_length=128, verbose_name='Ожидаемое значение ввода')),
                ('message', models.TextField(blank=True, default='required input', null=True, verbose_name='Сообщение для пользователя на экране ввода')),
                ('delay', models.IntegerField(blank=True, default=0, null=True, verbose_name='Задержка интерфейса пользователя')),
            ],
            options={
                'verbose_name': 'Пользовательский интерфейс ввода',
                'verbose_name_plural': 'Пользовательские интерфейсы ввода',
            },
        ),
        migrations.CreateModel(
            name='VideoFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('name', models.CharField(default='filename', max_length=128)),
                ('hash', models.CharField(default='', max_length=64)),
                ('file', models.FileField(storage=assets.storages.OverwriteStorage(location='/media/video'), upload_to='')),
            ],
            options={
                'verbose_name': 'Видео',
            },
        ),
    ]
