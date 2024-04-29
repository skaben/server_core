from core.helpers import get_uuid
from django.db import models


class UserInput(models.Model):

    uuid = models.UUIDField(primary_key=True, editable=False, default=get_uuid)

    action = models.CharField(
        default="action", blank=False, unique=True, max_length=64, verbose_name="Уникальное имя операции"
    )

    expected = models.CharField(default="", max_length=128, blank=True, verbose_name="Ожидаемое значение ввода")

    message = models.TextField(
        default="required input", verbose_name="Сообщение для пользователя на экране ввода", blank=True, null=True
    )

    delay = models.IntegerField(default=0, verbose_name="Задержка интерфейса пользователя", blank=True, null=True)

    class Meta:
        verbose_name = "Пользовательский интерфейс ввода"
        verbose_name_plural = "Пользовательские интерфейсы ввода"

    def __str__(self):
        return f"Input `{self.action}` required `{self.expected}`"
