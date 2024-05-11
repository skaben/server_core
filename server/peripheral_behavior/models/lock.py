from django.db import models


class LockBehavior(models.Model):
    """Laser lock device behavior."""

    class Meta:
        verbose_name = "Режим: лазерная дверь"
        verbose_name_plural = "Режимы: лазерные двери"

    sound = models.BooleanField(verbose_name="Звук замка", default=False)
    closed = models.BooleanField(verbose_name="Закрыт", default=True)
    blocked = models.BooleanField(verbose_name="Заблокирован", default=False)
    timer = models.IntegerField(verbose_name="Время автоматического закрытия", default=10)
