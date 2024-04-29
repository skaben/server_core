from typing import List, Literal, Optional, Union

from event_handling.alert.types import ALERT_COUNTER, ALERT_STATE
from alert.models import AlertCounter, AlertState


class AlertService:
    """Сервис управления счетчиком и уровнем тревоги."""

    states: dict
    state_ranges: dict
    min_alert_value: int
    max_scale_value: int
    init_by: str

    def __init__(self, init_by: Union[Literal[ALERT_COUNTER], Literal[ALERT_STATE], Literal["external"]] = "external"):  # type: ignore
        self.states = dict(enumerate(self.get_ingame_states()))
        self.state_ranges = self._calc_alert_ranges()
        self.min_alert_value = 1
        self.init_by = init_by
        self.max_scale_value = self.max_alert_value * 2

    def get_state_by_alert(self, alert_value: int) -> Optional[AlertState]:
        """Получает статус тревоги по значению счетчика тревоги"""
        if alert_value < 0:
            return

        for index, _range in self.state_ranges.items():
            if alert_value in range(*_range):
                return self.states.get(index)

    def get_state_by_name(self, name: str):
        """Получает статус тревоги по названию"""
        if not name:
            raise ValueError("alert state name not provided")
        return AlertState.objects.filter(name=name).first()

    def set_state_by_name(self, name: str):
        """Устанавливает статус тревоги по названию"""
        if not name:
            raise ValueError("alert state name not provided")
        instance = self.get_state_by_name(name)
        if instance:
            self.set_state_current(instance)

    def set_state_by_alert(self, value: int):
        """Устанавливает новое значение уровня тревоги по счетчику.

        Таким образом переключаются только ingame статусы.
        """
        current_state = self.get_state_current()
        alert_value = value if value < self.max_scale_value else self.max_alert_value
        new_state = self.get_state_by_alert(alert_value)

        if (
            new_state and new_state != current_state and
            new_state.ingame and current_state.ingame
        ):
            self.set_state_current(new_state)

    def change_alert_counter(self, value: int, increase: bool, comment: str | None = ""):
        """Уменьшает или увеличивает счетчик тревоги на значение"""
        latest = self.get_last_counter()
        new_value = latest + value if increase else latest - value
        self.set_alert_counter(new_value, comment)

    def set_state_current(self, instance: AlertState) -> AlertState:
        """Устанавливает значение уровня тревоги как текущее."""
        if not instance.current:
            instance.current = True
            instance.save(event_source=self.init_by)
        return instance

    def set_alert_counter(self, value: int, comment: str | None = "auto-change by alert service"):
        """Изменяет числовое значение счетчика тревоги.

        Приводит к изменению статуса тревоги, если значение попадает в диапазон значений срабатывания.
        """
        counter = AlertCounter(value=value, comment=comment)
        counter.save(event_source=self.init_by)

    def compare_threshold_by_name(self, level_name: str) -> bool:
        """Сравнивает трешхолд выбранного уровня с трешхолдом текущего"""
        new = AlertState.get_by_name(level_name)
        current = self.get_state_current()
        if not new:
            raise AlertState.DoesNotExist(f"cannot retrieve state by name {level_name}")
        return new.threshold > current.threshold

    def split_thresholds(self, count: int) -> List[int]:
        """Разделение диапазона уровня тревоги на равномерные диапазоны."""
        range_size = self.max_alert_value - self.min_alert_value
        sub_range_size = range_size / count
        thresholds = []
        threshold = self.min_alert_value
        for _ in range(count):
            threshold += sub_range_size
            thresholds.append(int(threshold))

        return thresholds

    def _calc_alert_ranges(self):
        """Вычисляет начальные и конечные уровни тревоги для каждого статуса"""
        result = {}
        self.state_ranges = dict()

        for index, item in self.states.items():
            nxt = self.states.get(index + 1)
            nxt_threshold = getattr(nxt, "threshold", self.max_scale_value)
            result.update({index: [item.threshold, nxt_threshold]})
        return result

    @property
    def max_alert_value(self) -> int:
        """Получает максимальное значение счетчика тревоги."""
        states = [state.threshold for state in AlertState.objects.all().order_by("threshold")]
        return max(states) if states else self.min_alert_value

    @staticmethod
    def get_state_current() -> AlertState:
        """Получает текущий статус тревоги."""
        return AlertState.objects.filter(current=True).get()

    @staticmethod
    def get_last_counter() -> int:
        """Получает последний счетчик тревоги."""
        try:
            counter = AlertCounter.objects.latest("id")
        except AlertCounter.DoesNotExist:
            counter = AlertCounter(value=0, comment="initial counter set by AlertService")
            counter.save()
        return counter.value

    @staticmethod
    def get_ingame_states(sort_by: str | None = "order"):
        """Получает все внутриигровые статусы"""
        return AlertState.objects.filter(ingame=True).order_by(sort_by).all()

    def __str__(self):
        return "AlertService"

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return
