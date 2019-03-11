# Generated by Django 2.1.7 on 2019-03-07 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iface', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dumb',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ts', models.IntegerField(default=1551980171)),
                ('config', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Lock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ts', models.IntegerField(default=1551980172)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('ip', models.CharField(max_length=30)),
                ('override', models.BooleanField(default=False)),
                ('sound', models.BooleanField(default=False)),
                ('opened', models.BooleanField(default=False)),
                ('allowed', models.CharField(max_length=300)),
            ],
        ),
        migrations.DeleteModel(
            name='DumbModel',
        ),
        migrations.DeleteModel(
            name='LockModel',
        ),
    ]
