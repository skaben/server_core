from django.db import models
from peripheral_devices.models.base import SkabenDevice
from peripheral_devices.serializers.schema import TerminalDeviceSchema

__all__ = ("TerminalDevice",)


class TerminalDevice(SkabenDevice):
    """Smart terminal."""

    class Meta:
        verbose_name = "Терминал"
        verbose_name_plural = "Терминалы"

    account_set = models.ManyToManyField("peripheral_behavior.TerminalAccount")

    @property
    def topic(self) -> str:
        return "terminal"

    def to_mqtt_config(self):
        validated_base = super().to_mqtt_config()
        to_be_validated = dict(
            blocked=self.blocked,
            powered=self.powered,
        )
        schema = TerminalDeviceSchema.model_validate(validated_base | to_be_validated)
        return schema.dict()

    def get_hash(self) -> str:
        watch_list = ["alert", "powered", "blocked"]
        return super().hash_from_attrs(watch_list)

    def __str__(self):
        return f"Терминал <{self.mac_addr}> [ip: {self.ip}] {self.description}"
