# Generated by Django 5.0.3 on 2024-05-11 19:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('alert', '0001_initial'),
        ('assets', '0001_initial'),
        ('peripheral_behavior', '0001_initial'),
        ('peripheral_devices', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='permission',
            name='lock',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='peripheral_devices.lockdevice', verbose_name='Замок'),
        ),
        migrations.AddField(
            model_name='permission',
            name='state_id',
            field=models.ManyToManyField(to='alert.alertstate', verbose_name='Уровень тревоги'),
        ),
        migrations.AddField(
            model_name='accesscode',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='peripheral_behavior.skabenuser'),
        ),
        migrations.AddField(
            model_name='terminalaccount',
            name='menu_items',
            field=models.ManyToManyField(related_name='menu_items', to='peripheral_behavior.menuitem'),
        ),
        migrations.AddField(
            model_name='terminalaccount',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='peripheral_behavior.skabenuser', verbose_name='Пользователь'),
        ),
        migrations.AddField(
            model_name='terminalmenuset',
            name='account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='peripheral_behavior.terminalaccount', verbose_name='Аккаунт'),
        ),
        migrations.AddField(
            model_name='terminalmenuset',
            name='state_id',
            field=models.ManyToManyField(to='alert.alertstate', verbose_name='Уровень тревоги'),
        ),
        migrations.AddField(
            model_name='terminalmenuset',
            name='terminal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='peripheral_devices.terminaldevice', verbose_name='Терминал'),
        ),
        migrations.AddField(
            model_name='menuitemaudio',
            name='content',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assets.audiofile', verbose_name='Связанное аудио'),
        ),
        migrations.AddField(
            model_name='menuitemimage',
            name='content',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assets.imagefile', verbose_name='Связанное изображение'),
        ),
        migrations.AddField(
            model_name='menuitemtext',
            name='content',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assets.textfile', verbose_name='Связанный текст'),
        ),
        migrations.AddField(
            model_name='menuitemuserinput',
            name='content',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assets.userinput', verbose_name='Пользовательский ввод'),
        ),
        migrations.AddField(
            model_name='menuitemvideo',
            name='content',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assets.videofile', verbose_name='Связанное видео'),
        ),
        migrations.AlterUniqueTogether(
            name='permission',
            unique_together={('card', 'lock')},
        ),
    ]