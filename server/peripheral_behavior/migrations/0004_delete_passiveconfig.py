# Generated by Django 5.0.3 on 2024-05-10 17:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('peripheral_behavior', '0003_passiveconfig_comment'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PassiveConfig',
        ),
    ]
