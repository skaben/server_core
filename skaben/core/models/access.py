from django.db import models
from .alert import AlertState
from .device import Lock


class AccessCode(models.Model):
    """In-game access code or card id"""

    class Meta:
        verbose_name = 'Игровой код доступа'
        verbose_name_plural = 'Игровые коды доступа'

    code = models.CharField(max_length=8)
    name = models.CharField(max_length=64)
    surname = models.CharField(max_length=64)
    position = models.CharField(max_length=128)

    def __str__(self):
        return f'<{self.code}> {self.position} {self.surname}'


class Permission(models.Model):
    """Access codes permission to open locks"""

    class Meta:
        unique_together = ('card', 'lock')
        verbose_name = 'Игровые права доступа карт'
        verbose_name_plural = 'Игровые права доступа карт'

    card = models.ForeignKey(AccessCode, on_delete=models.CASCADE)
    lock = models.ForeignKey(Lock, on_delete=models.CASCADE)
    state_id = models.ManyToManyField(AlertState)

    def __str__(self):
        return f'[ {self.lock.info.upper()} ] {self.card.position} ' \
               f'{self.card.surname} '
