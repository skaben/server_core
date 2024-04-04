# Generated by Django 4.2 on 2023-05-21 19:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("alert", "0002_alter_alertstate_modifier_alter_alertstate_order_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="alertstate",
            name="auto_decrease",
            field=models.IntegerField(
                default=0,
                help_text="Уменьшается ли уровень со временем (settings.ALERT_COOLDOWN). Значение 0 выключает параметр",
                verbose_name="Применяется ли авто-сброс тревоги",
            ),
        ),
        migrations.AddField(
            model_name="alertstate",
            name="auto_increase",
            field=models.IntegerField(
                default=0,
                help_text="Увеличивается ли уровень со временем (settings.ALERT_COOLDOWN). Значение 0 выключает параметр",
                verbose_name="Авто-увеличение уровня тревоги",
            ),
        ),
    ]