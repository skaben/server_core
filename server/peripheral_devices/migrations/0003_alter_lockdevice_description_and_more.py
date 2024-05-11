
import core.helpers
import peripheral_devices.validators
import core.helpers
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('peripheral_devices', '0002_alter_lockdevice_mac_addr_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lockdevice',
            name='description',
            field=models.CharField(default='smart complex device', max_length=128, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='lockdevice',
            name='mac_addr',
            field=models.CharField(max_length=12, unique=True, validators=[peripheral_devices.validators.mac_validator], verbose_name='MAC'),
        ),
        migrations.AlterField(
            model_name='lockdevice',
            name='override',
            field=models.BooleanField(default=False, verbose_name='Отключить авто-обновление'),
        ),
        migrations.AlterField(
            model_name='lockdevice',
            name='timestamp',
            field=models.IntegerField(default=core.helpers.get_server_timestamp, verbose_name='Время последнего ответа'),
        ),
        migrations.AlterField(
            model_name='terminaldevice',
            name='description',
            field=models.CharField(default='smart complex device', max_length=128, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='terminaldevice',
            name='mac_addr',
            field=models.CharField(max_length=12, unique=True, validators=[peripheral_devices.validators.mac_validator], verbose_name='MAC'),
        ),
        migrations.AlterField(
            model_name='terminaldevice',
            name='override',
            field=models.BooleanField(default=False, verbose_name='Отключить авто-обновление'),
        ),
        migrations.AlterField(
            model_name='terminaldevice',
            name='timestamp',
            field=models.IntegerField(default=core.helpers.get_server_timestamp, verbose_name='Время последнего ответа'),
        ),
    ]
