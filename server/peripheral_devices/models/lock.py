from django.db import models
from peripheral_devices.models.base import SkabenDevice

__all__ = ("LockDevice",)


class LockDevice(SkabenDevice):
    """Laser lock device."""

    class Meta:
        verbose_name = "Лазерная дверь"
        verbose_name_plural = "Лазерные двери"

    sound = models.BooleanField(verbose_name="Звук замка", default=False)
    closed = models.BooleanField(verbose_name="Закрыт", default=True)
    blocked = models.BooleanField(verbose_name="Заблокирован", default=False)
    timer = models.IntegerField(verbose_name="Время автоматического закрытия", default=10)

    def permissions(self) -> dict:
        """Получает словарь связанных карт-кодов и статусов тревоги, в которых они открывают замок."""
        acl = {}
        permission_set = self.permission_set.prefetch_related("card", "state_id").filter(lock_id=self.id)
        for perm in permission_set:
            state_list = [state.id for state in perm.state_id.all()]
            acl[f"{perm.card.code}"] = state_list
        return acl

    def get_hash(self) -> str:
        watch_list = ["closed", "blocked", "sound"]
        return super()._hash(watch_list)

    @property
    def topic(self):
        """Получает MQTT-топик."""
        return "lock"

    def __str__(self):
        """Строковое представление модели."""
        return f"LOCK [ip: {self.ip}] {self.description[:10]}"
