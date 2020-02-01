# Generated by Django 2.2.6 on 2019-10-23 09:51

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20191021_1210'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tamed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ts', models.IntegerField(default=1571824262)),
                ('uid', models.CharField(max_length=16, unique=True)),
                ('descr', models.CharField(default='simple dumb', max_length=255)),
                ('online', models.BooleanField(default=False)),
                ('ip', models.GenericIPAddressField()),
                ('subtype', models.CharField(default='rgb', max_length=32)),
                ('config', models.ManyToManyField(default='noop', to='core.ConfigString')),
            ],
            options={
                'verbose_name': 'Устройство пассивное',
                'verbose_name_plural': 'Устройства пассивные',
            },
            bases=(models.Model, core.models.DeviceMixin),
        ),
        migrations.AlterField(
            model_name='alertcounter',
            name='timestamp',
            field=models.IntegerField(default=1571824262),
        ),
        migrations.AlterField(
            model_name='eventlog',
            name='timestamp',
            field=models.IntegerField(default=1571824262),
        ),
        migrations.AlterField(
            model_name='lock',
            name='ts',
            field=models.IntegerField(default=1571824262),
        ),
        migrations.AlterField(
            model_name='terminal',
            name='ts',
            field=models.IntegerField(default=1571824262),
        ),
        migrations.DeleteModel(
            name='Dumb',
        ),
    ]