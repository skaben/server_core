# Generated by Django 2.2.12 on 2020-05-28 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0056_auto_20200528_0650'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alertcounter',
            name='timestamp',
            field=models.IntegerField(default=1590649247),
        ),
        migrations.AlterField(
            model_name='eventlog',
            name='timestamp',
            field=models.IntegerField(default=1590649247),
        ),
        migrations.AlterField(
            model_name='lock',
            name='timestamp',
            field=models.IntegerField(default=1590649247),
        ),
        migrations.AlterField(
            model_name='mqttmessage',
            name='timestamp',
            field=models.IntegerField(default=1590649247),
        ),
        migrations.AlterField(
            model_name='tamed',
            name='timestamp',
            field=models.IntegerField(default=1590649247),
        ),
        migrations.AlterField(
            model_name='terminal',
            name='timestamp',
            field=models.IntegerField(default=1590649247),
        ),
    ]
