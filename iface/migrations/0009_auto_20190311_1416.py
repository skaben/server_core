# Generated by Django 2.1.7 on 2019-03-11 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iface', '0008_auto_20190311_1413'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dumb',
            name='ts',
            field=models.IntegerField(default=1552313797),
        ),
        migrations.AlterField(
            model_name='lock',
            name='ts',
            field=models.IntegerField(default=1552313797),
        ),
        migrations.AlterField(
            model_name='terminal',
            name='ts',
            field=models.IntegerField(default=1552313797),
        ),
    ]
