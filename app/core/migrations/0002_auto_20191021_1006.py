# Generated by Django 2.2.6 on 2019-10-21 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dumb',
            name='dev_subtype',
        ),
        migrations.AddField(
            model_name='dumb',
            name='config',
            field=models.ManyToManyField(default='noop', to='core.ConfigString'),
        ),
        migrations.AddField(
            model_name='dumb',
            name='subtype',
            field=models.CharField(default='rgb', max_length=32),
        ),
        migrations.AlterField(
            model_name='alertcounter',
            name='timestamp',
            field=models.IntegerField(default=1571652363),
        ),
        migrations.AlterField(
            model_name='dumb',
            name='descr',
            field=models.CharField(default='simple dumb', max_length=255),
        ),
        migrations.AlterField(
            model_name='dumb',
            name='ts',
            field=models.IntegerField(default=1571652363),
        ),
        migrations.AlterField(
            model_name='eventlog',
            name='timestamp',
            field=models.IntegerField(default=1571652363),
        ),
        migrations.AlterField(
            model_name='lock',
            name='ts',
            field=models.IntegerField(default=1571652363),
        ),
        migrations.AlterField(
            model_name='terminal',
            name='ts',
            field=models.IntegerField(default=1571652363),
        ),
    ]
