# Generated by Django 4.2 on 2023-05-20 17:17

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("peripheral_behavior", "0004_alter_passiveconfig_topic"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="passiveconfig",
            options={
                "verbose_name": "Пассивное устройство",
                "verbose_name_plural": "Пассивные устройства",
            },
        ),
    ]
