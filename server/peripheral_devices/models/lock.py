from django.db import models
from peripheral_devices.models.base import SkabenDevice

__all__ = (
    'LockDevice',
)


class LockDevice(SkabenDevice):
    """Laser lock device."""

    class Meta:
        verbose_name = 'Лазерная дверь'
        verbose_name_plural = 'Лазерные двери'

    sound = models.BooleanField(default=False)
    closed = models.BooleanField(default=True)
    blocked = models.BooleanField(default=False)
    timer = models.IntegerField(default=10)

    @property
    def acl(self) -> dict:
        # unload list of Card codes for lock end-device
        acl = {}
        for perm in self.permission_set.filter(lock_id=self.id):
            state_list = [state.id for state in perm.state_id.all()]
            acl[f"{perm.card.code}"] = state_list
        return acl

    @property
    def topic(self):
        return 'lock'

    def __str__(self):
        return f'LOCK [ip: {self.ip}] {self.description}'
