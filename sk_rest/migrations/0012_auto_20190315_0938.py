# Generated by Django 2.1.7 on 2019-03-15 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sk_rest', '0011_auto_20190311_1420'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dumb',
            options={'verbose_name': 'device: RGB (Dumb)', 'verbose_name_plural': 'devices: RGB (Dumbs)'},
        ),
        migrations.RemoveField(
            model_name='lock',
            name='name',
        ),
        migrations.RemoveField(
            model_name='terminal',
            name='name',
        ),
        migrations.AddField(
            model_name='dumb',
            name='descr',
            field=models.CharField(default='', max_length=120),
        ),
        migrations.AddField(
            model_name='dumb',
            name='online',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='lock',
            name='descr',
            field=models.CharField(default='', max_length=120),
        ),
        migrations.AddField(
            model_name='lock',
            name='online',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='terminal',
            name='descr',
            field=models.CharField(default='', max_length=120),
        ),
        migrations.AddField(
            model_name='terminal',
            name='online',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='dumb',
            name='ts',
            field=models.IntegerField(default=1552642722),
        ),
        migrations.AlterField(
            model_name='lock',
            name='ts',
            field=models.IntegerField(default=1552642722),
        ),
        migrations.AlterField(
            model_name='terminal',
            name='ts',
            field=models.IntegerField(default=1552642722),
        ),
    ]
