# Generated by Django 2.2.12 on 2020-05-27 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0039_auto_20200527_1744'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alertcounter',
            name='timestamp',
            field=models.IntegerField(default=1590601701),
        ),
        migrations.AlterField(
            model_name='eventlog',
            name='timestamp',
            field=models.IntegerField(default=1590601701),
        ),
        migrations.AlterField(
            model_name='lock',
            name='timestamp',
            field=models.IntegerField(default=1590601701),
        ),
        migrations.AlterField(
            model_name='mqttmessage',
            name='timestamp',
            field=models.IntegerField(default=1590601701),
        ),
        migrations.AlterField(
            model_name='tamed',
            name='timestamp',
            field=models.IntegerField(default=1590601701),
        ),
        migrations.AlterField(
            model_name='terminal',
            name='timestamp',
            field=models.IntegerField(default=1590601701),
        ),
    ]
