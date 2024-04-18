from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from core.transport.publish import get_interface


class AlertCounter(models.Model):
    """In-game Global Alert State counter"""

    class Meta:
        verbose_name = "Тревога: счетчик уровня"
        verbose_name_plural = "Тревога: счетчик уровня"

    value = models.IntegerField(
        verbose_name="Значение счетчика",
        help_text="Счетчик примет указанное значение, уровень тревоги может быть сброшен",
        default=0,
    )
    comment = models.CharField(
        verbose_name="Причина изменений",
        default="reason: changed by admin",
        max_length=64,
    )
    timestamp = models.DateTimeField(
        verbose_name="Время последнего изменения",
        default=timezone.now,
    )

    def save(self, *args, **kwargs):
        """Сохранение, связывающее модели AlertCounter и AlertState."""
        prev_alert_counter = AlertCounter.objects.order_by("-id").first()
        prev_value = 0 if not prev_alert_counter else prev_alert_counter.value

        super().save(*args, **kwargs)
        with get_interface() as mq_interface:
            mq_interface.send_event(
                "alert_counter",
                {
                    "counter": self.value,
                    "increased": prev_value < self.value,
                },
            )

    def __str__(self):
        return f"{self.value} {self.comment} at {self.timestamp}"


class AlertState(models.Model):
    """In-game Global Alert State"""

    __original_state = None

    class Meta:
        verbose_name = "Тревога: именной статус"
        verbose_name_plural = "Тревога: именные статусы"

    name = models.CharField(verbose_name="Название статуса", max_length=32, blank=False, unique=True)
    info = models.CharField(verbose_name="Описание статуса", max_length=256)
    ingame = models.BooleanField(
        verbose_name="Игровой статус",
        help_text=(
            "Будет ли статус автоматически изменяться системой счетчика тревоги, "
            "или переключиться в него можно только специальным событием или вручную. "
        ),
        default=True,
    )
    threshold = models.IntegerField(
        verbose_name="Порог срабатывания ",
        help_text=(
            "Нижнее значение счетчика счетчика тревоги для переключения в статус. "
            "Чтобы отключить авто-переключение - выставьте отрицательное значение"
        ),
        default=-1,
    )
    current = models.BooleanField(verbose_name="Сейчас активен", default=False)
    order = models.IntegerField(
        verbose_name="Цифровой id статуса",
        help_text="используется для идентификации и упорядочивания статуса без привязки к id в БД",
        blank=False,
        unique=True,
    )

    auto_increase = models.BooleanField(
        verbose_name="Авто-увеличение тревоги",
        help_text=("Включить автоматическое повышение тревоги со временем"),
        default=False,
    )

    auto_decrease = models.BooleanField(
        verbose_name="Авто-уменьшение тревоги",
        help_text=("Включить автоматическое повышение тревоги со временем"),
        default=False,
    )

    counter_increase = models.IntegerField(
        verbose_name="На сколько увеличить уровень тревоги",
        help_text=(
            "Цена ошибки. Также определяет на сколько увеличится уровень "
            "со временем (settings.ALERT_COOLDOWN) автоматически."
        ),
        default=0,
    )

    counter_decrease = models.IntegerField(
        verbose_name="На сколько уменьшить уровень тревоги",
        help_text=(
            "Насколько снизится уровень тревоги при действии. Также определяет, на сколько уменьшится уровень "
            "со временем (settings.ALERT_COOLDOWN) автоматически."
        ),
        default=0,
    )

    def __init__(self, *args, **kwargs):
        super(AlertState, self).__init__(*args, **kwargs)
        self.__original_state = self.current

    @property
    def is_final(self):
        states = AlertState.objects.all().order_by("order")
        return states.last().id == self.id

    @property
    def get_current(self):
        if self.current:
            return self
        return AlertState.objects.all().filter(current=True).first()

    @staticmethod
    def get_by_name(name: str):
        return AlertState.objects.filter(name=name).first()

    def clean(self):
        has_current = AlertState.objects.all().exclude(pk=self.id).filter(current=True)
        if not self.current and not has_current:
            raise ValidationError("cannot unset current - no other current states")

    def save(self, *args, **kwargs):
        """Сохранение, связывающее модели AlertCounter и AlertState."""
        if self.current and not self.__original_state:
            other_states = AlertState.objects.all().exclude(pk=self.id)
            other_states.update(current=False)

        super().save(*args, **kwargs)

        if self.__original_state != self.current:
            with get_interface() as mq_interface:
                mq_interface.send_event("alert_state", {"state": self.name})
        self.__original_state = self.current

    is_final.fget.short_description = "Финальный игровой статус"

    def __str__(self):
        s = f"[{self.order}] State: {self.name} ({self.info})"
        if self.current:
            return "===ACTIVE===" + s + "===ACTIVE==="
        else:
            return s
