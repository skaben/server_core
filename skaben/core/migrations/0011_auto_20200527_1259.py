# Generated by Django 2.2.12 on 2020-05-27 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20200508_1659'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alertcounter',
            name='timestamp',
            field=models.IntegerField(default=1590584358),
        ),
        migrations.AlterField(
            model_name='eventlog',
            name='timestamp',
            field=models.IntegerField(default=1590584358),
        ),
        migrations.AlterField(
            model_name='lock',
            name='ts',
            field=models.IntegerField(default=1590584358),
        ),
        migrations.AlterField(
            model_name='mqttmessage',
            name='timestamp',
            field=models.IntegerField(default=1590584358),
        ),
        migrations.AlterField(
            model_name='tamed',
            name='ts',
            field=models.IntegerField(default=1590584358),
        ),
        migrations.AlterField(
            model_name='terminal',
            name='ts',
            field=models.IntegerField(default=1590584358),
        ),
    ]
