from django.db import models

__all__ = [
    'User',
    'AccessCode',
    'Permission'
]


class User(models.Model):
    """User model."""

    class Meta:
        verbose_name = 'Игровой пользователь'
        verbose_name_plural = 'Игровые пользователи'

    name = models.CharField(max_length=128)
    description = models.CharField(max_length=128)


class AccessCode(models.Model):
    """User access code."""

    class Meta:
        verbose_name = 'Код доступа (ключ-карта)'
        verbose_name_plural = 'Коды доступа (ключ-карты)'

    code = models.CharField(max_length=8)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'<{self.code}> {self.user.name}'


class Permission(models.Model):
    """Access codes permission to open locks."""

    class Meta:
        unique_together = ('card', 'lock')
        verbose_name = 'Доступ ключ-карты (права)'
        verbose_name_plural = 'Доступы ключ-карт (права)'

    card = models.ForeignKey('peripherals.AccessCode', on_delete=models.CASCADE)
    lock = models.ForeignKey('peripherals.Lock', on_delete=models.CASCADE)
    state_id = models.ManyToManyField('alert.AlertState')
