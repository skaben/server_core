# Generated by Django 5.0.3 on 2024-05-11 17:46

import core.helpers
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='StreamRecord',
            fields=[
                ('uuid', models.UUIDField(default=core.helpers.get_uuid, editable=False, primary_key=True, serialize=False)),
                ('timestamp', models.IntegerField(default=core.helpers.get_server_timestamp)),
                ('message', models.CharField(help_text='Название события')),
                ('message_data', models.JSONField(blank=True, default=dict, help_text='Содержимое события', null=True)),
                ('stream', models.CharField(default='game', help_text='Поток события', max_length=256)),
                ('source', models.CharField(default='default', help_text='Источник события', max_length=256)),
                ('mark', models.CharField(blank=True, help_text='Дополнительный маркер события', max_length=32)),
            ],
            options={
                'verbose_name': 'Игровое событие',
                'verbose_name_plural': 'Игровые события',
            },
        ),
    ]
