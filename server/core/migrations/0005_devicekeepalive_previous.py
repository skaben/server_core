# Generated by Django 4.2 on 2023-05-20 18:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_devicekeepalive"),
    ]

    operations = [
        migrations.AddField(
            model_name="devicekeepalive",
            name="previous",
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
