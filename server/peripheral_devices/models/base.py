import logging
from alert.models import AlertState
from core.helpers import get_server_timestamp, get_hash_from
from django.conf import settings
from django.db import models
from core.transport.publish import get_interface
from peripheral_devices.validators import mac_validator
from peripheral_devices.serializers.schema import BaseDeviceSchema
from peripheral_devices.service.packet_format import cup_packet_from_model


class SkabenDeviceManager(models.Manager):
    def not_overridden(self):
        return self.get_queryset().exclude(override=True)


class SkabenDevice(models.Model):
    """Abstract device."""

    objects = SkabenDeviceManager()

    class Meta:
        abstract = True

    ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP-адрес")
    mac_addr = models.CharField(max_length=12, unique=True, verbose_name="MAC", validators=[mac_validator])
    description = models.CharField(max_length=128, default="smart complex device", verbose_name="Описание")
    timestamp = models.IntegerField(default=get_server_timestamp, verbose_name="Время последнего ответа")
    override = models.BooleanField(default=False, verbose_name="Отключить авто-обновление")

    @property
    def online(self) -> bool:
        return self.timestamp + settings.DEVICE_KEEPALIVE_TIMEOUT > get_server_timestamp()

    online.fget.short_description = "Онлайн"

    @property
    def alert(self) -> str:
        state = AlertState.objects.get_current()
        return str(getattr(state, "id", ""))

    alert.fget.short_description = "Уровень тревоги"

    @property
    def topic(self) -> str:
        raise NotImplementedError("abstract class property")

    topic.fget.short_description = "MQTT-топик"

    def to_mqtt_config(self):
        # todo: remove double validation in inherited models
        schema = BaseDeviceSchema.model_validate(
            dict(
                alert=self.alert,
                override=self.override,
            )
        )
        return schema.dict()

    def hash_from_attrs(self, attrs: list[str]) -> str:
        return get_hash_from({attr: getattr(self, attr) for attr in attrs})

    def get_hash(self) -> str:
        return get_hash_from(list(self.__dict__.keys()))

    def _send_update(self):
        if self.override:
            logging.warning("Device %s <%s> is under override rule", self.topic, self.mac_addr)
        else:
            packet = cup_packet_from_model(self)
            with get_interface() as interface:
                interface.send_mqtt(packet)

    def save(self, *args, **kwargs):
        """Сохранение, отправляющее конфиг устройству, если передан параметр send_update=True."""
        send_update = True

        if kwargs.get("send_update"):
            send_update = kwargs.pop("send_update")

        super().save(*args, **kwargs)

        if send_update:
            self._send_update()
