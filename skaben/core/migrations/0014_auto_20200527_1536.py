# Generated by Django 2.2.12 on 2020-05-27 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20200527_1347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alertcounter',
            name='timestamp',
            field=models.IntegerField(default=1590593780),
        ),
        migrations.AlterField(
            model_name='eventlog',
            name='timestamp',
            field=models.IntegerField(default=1590593780),
        ),
        migrations.AlterField(
            model_name='lock',
            name='ts',
            field=models.IntegerField(default=1590593780),
        ),
        migrations.AlterField(
            model_name='mqttmessage',
            name='timestamp',
            field=models.IntegerField(default=1590593780),
        ),
        migrations.AlterField(
            model_name='tamed',
            name='ts',
            field=models.IntegerField(default=1590593780),
        ),
        migrations.AlterField(
            model_name='terminal',
            name='ts',
            field=models.IntegerField(default=1590593780),
        ),
    ]
