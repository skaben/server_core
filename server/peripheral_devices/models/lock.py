from django.db import models
from alert.service import AlertState
from peripheral_devices.models.base import SkabenDevice
from peripheral_devices.serializers.schema import LockDeviceSchema

__all__ = ("LockDevice",)


class LockDevice(SkabenDevice):
    """Laser lock device."""

    class Meta:
        verbose_name = "Лазерная дверь"
        verbose_name_plural = "Лазерные двери"

    work_mode = models.ManyToManyField("peripheral_behavior.LockWorkMode")

    def permissions(self) -> dict:
        """Получает словарь связанных карт-кодов и статусов тревоги, в которых они открывают замок."""
        acl = {}
        permission_set = self.permission_set.prefetch_related("card", "state_id").filter(lock_id=self.id)
        for perm in permission_set:
            state_list = [state.id for state in perm.state_id.all()]
            acl[f"{perm.card.code}"] = state_list
        return acl

    def get_hash(self) -> str:
        watch_list = ["closed", "blocked", "sound", "alert", "override"]
        return super().hash_from_attrs(watch_list)

    def to_mqtt_config(self):
        validated_base = super().to_mqtt_config()
        current = AlertState.objects.get_current()
        work_mode = self.work_mode.filter(state_id__pk=current.id)
        if not work_mode:
            return  # todo: add defaults
        to_be_validated = dict(
            sound=work_mode.sound,
            timer=work_mode.timer,
            closed=work_mode.closed,
            blocked=work_mode.blocked,
            permissions=self.permissions(),
        )
        schema = LockDeviceSchema.model_validate(validated_base | to_be_validated)
        return schema.dict()

    @property
    def topic(self):
        """Получает MQTT-топик."""
        return "lock"

    def __str__(self):
        """Строковое представление модели."""
        return f"Замок <{self.mac_addr}> [ip: {self.ip}] {self.description}"
