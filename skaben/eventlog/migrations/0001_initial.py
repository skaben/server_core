# Generated by Django 3.2 on 2021-04-25 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EventLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.IntegerField(default=1619356123)),
                ('level', models.CharField(default='info', max_length=32)),
                ('access', models.CharField(default='root', max_length=32)),
                ('message', models.TextField()),
            ],
            options={
                'verbose_name': 'База: Хроника событий',
                'verbose_name_plural': 'База: Хроника событий',
            },
        ),
    ]
