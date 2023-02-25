# Generated by Django 4.1.7 on 2023-02-25 18:06

import core.helpers
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LockDevice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP-адрес')),
                ('mac_addr', models.CharField(max_length=16, unique=True)),
                ('description', models.CharField(default='smart complex device', max_length=128)),
                ('timestamp', models.IntegerField(default=core.helpers.get_server_timestamp)),
                ('override', models.BooleanField(default=False)),
                ('sound', models.BooleanField(default=False)),
                ('closed', models.BooleanField(default=True)),
                ('blocked', models.BooleanField(default=False)),
                ('timer', models.IntegerField(default=10)),
            ],
            options={
                'verbose_name': 'Лазерная дверь',
                'verbose_name_plural': 'Лазерные двери',
            },
        ),
        migrations.CreateModel(
            name='SimpleDevice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP-адрес')),
                ('mac_addr', models.CharField(max_length=16, unique=True)),
                ('description', models.CharField(default='smart complex device', max_length=128)),
                ('timestamp', models.IntegerField(default=core.helpers.get_server_timestamp)),
                ('override', models.BooleanField(default=False)),
                ('channel', models.CharField(max_length=16)),
            ],
            options={
                'verbose_name': 'Пассивное устройство',
                'verbose_name_plural': 'Пассивные устройства',
            },
        ),
        migrations.CreateModel(
            name='TerminalDevice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP-адрес')),
                ('mac_addr', models.CharField(max_length=16, unique=True)),
                ('description', models.CharField(default='smart complex device', max_length=128)),
                ('timestamp', models.IntegerField(default=core.helpers.get_server_timestamp)),
                ('override', models.BooleanField(default=False)),
                ('powered', models.BooleanField(default=False)),
                ('blocked', models.BooleanField(default=False)),
                ('hacked', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Терминал',
                'verbose_name_plural': 'Терминалы',
            },
        ),
    ]
