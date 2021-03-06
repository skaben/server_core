# Generated by Django 3.2 on 2021-04-25 13:08

import device.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Lock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(max_length=16, unique=True)),
                ('info', models.CharField(default='smart complex device', max_length=128)),
                ('ip', models.GenericIPAddressField(blank=True, null=True)),
                ('timestamp', models.IntegerField(default=1619356123)),
                ('override', models.BooleanField(default=False)),
                ('sound', models.BooleanField(default=False)),
                ('closed', models.BooleanField(default=True)),
                ('blocked', models.BooleanField(default=False)),
                ('timer', models.IntegerField(default=10)),
            ],
            options={
                'verbose_name': 'Клиент (устройство) Замок',
                'verbose_name_plural': 'Клиент (устройство) Замки',
            },
            bases=(models.Model, device.models.DeviceMixin),
        ),
        migrations.CreateModel(
            name='Simple',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.IntegerField(default=1619356123)),
                ('uid', models.CharField(max_length=16, unique=True)),
                ('ip', models.GenericIPAddressField(blank=True, null=True)),
                ('dev_type', models.CharField(max_length=16)),
            ],
            options={
                'verbose_name': 'Клиент пассивный',
                'verbose_name_plural': 'Клиенты пассивные',
            },
            bases=(models.Model, device.models.DeviceMixin),
        ),
        migrations.CreateModel(
            name='Terminal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(max_length=16, unique=True)),
                ('info', models.CharField(default='smart complex device', max_length=128)),
                ('ip', models.GenericIPAddressField(blank=True, null=True)),
                ('timestamp', models.IntegerField(default=1619356123)),
                ('override', models.BooleanField(default=False)),
                ('powered', models.BooleanField(default=False)),
                ('blocked', models.BooleanField(default=False)),
                ('hacked', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Клиент (устройство) Терминал',
                'verbose_name_plural': 'Клиент (устройство) Терминалы',
            },
            bases=(models.Model, device.models.DeviceMixin),
        ),
    ]
