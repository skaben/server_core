# Generated by Django 3.2 on 2021-04-25 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shape', '0001_initial'),
        ('device', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='terminal',
            name='modes_extended',
            field=models.ManyToManyField(blank=True, default=None, related_name='mode_extended', to='shape.WorkMode'),
        ),
        migrations.AddField(
            model_name='terminal',
            name='modes_normal',
            field=models.ManyToManyField(blank=True, default=None, related_name='mode_normal', to='shape.WorkMode'),
        ),
    ]
