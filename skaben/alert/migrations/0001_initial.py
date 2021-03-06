# Generated by Django 3.2 on 2021-04-25 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AlertCounter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField(default=0)),
                ('comment', models.CharField(default='changed by admin', max_length=256)),
                ('timestamp', models.IntegerField(default=1619356123)),
            ],
            options={
                'verbose_name': 'Тревога: счетчик уровня',
                'verbose_name_plural': 'Тревога: счетчик уровня',
            },
        ),
        migrations.CreateModel(
            name='AlertState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True)),
                ('info', models.CharField(max_length=256)),
                ('bg_color', models.CharField(default='#000000', max_length=7)),
                ('fg_color', models.CharField(default='#ffffff', max_length=7)),
                ('threshold', models.IntegerField(default=-1)),
                ('current', models.BooleanField(default=False)),
                ('order', models.IntegerField(unique=True)),
                ('modifier', models.IntegerField(default=5)),
            ],
            options={
                'verbose_name': 'Тревога: именной статус',
                'verbose_name_plural': 'Тревога: именные статусы',
            },
        ),
    ]
