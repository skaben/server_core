# Generated by Django 5.0.3 on 2024-04-01 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("peripheral_devices", "0002_delete_simpledevice"),
    ]

    operations = [
        migrations.AlterField(
            model_name="lockdevice",
            name="blocked",
            field=models.BooleanField(default=False, verbose_name="Заблокирован"),
        ),
        migrations.AlterField(
            model_name="lockdevice",
            name="closed",
            field=models.BooleanField(default=True, verbose_name="Закрыт"),
        ),
        migrations.AlterField(
            model_name="lockdevice",
            name="sound",
            field=models.BooleanField(default=False, verbose_name="Звук замка"),
        ),
        migrations.AlterField(
            model_name="lockdevice",
            name="timer",
            field=models.IntegerField(
                default=10, verbose_name="Время автоматического закрытия"
            ),
        ),
    ]