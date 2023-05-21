import logging

from operator import itemgetter
from typing import List

from alert.models import (
    AlertCounter,
    AlertState,
)


class AlertService:
    """ Global Alert mutation service """

    states: dict
    state_ranges: dict
    min_alert_value: int

    def __init__(self):
        self.states = {}
        self.state_ranges = {}
        self.min_alert_value = 1

    def reset_state(self, name: str | None = ''):
        """Сбрасывает состояние до указанного или до минимального игрового"""
        if name:
            self.set_state_by_name(name)
        else:
            in_game = self._get_ingame_states()
            self.set_state_current(in_game[0])

    def reset_counter(self, level: int | None = None, comment: str | None = None):
        """Сбрасывает тревогу до указанного или минимального игрового"""
        if not level:
            level = self.min_alert_value
        self.set_alert_counter(value=level, comment=comment)

    def get_state_by_alert(self, alert_value: int):
        """Получает статус тревоги по значению счетчика тревоги"""
        logging.debug(f'{self} getting state by alert value: {alert_value}')
        if not self.state_ranges:
            self.state_ranges = self._calc_alert_ranges()

        for index, _range in self.state_ranges.items():
            if alert_value in range(*_range):
                return self.states.get(index)

    def set_state_by_name(self, name: str):
        """Устанавливает статус тревоги по названию"""
        try:
            instance = AlertState.objects.filter(name=name).first()
            self.set_state_current(instance)
        except AlertState.DoesNotExist:
            raise

    def change_alert_counter(self, value: int, increase: bool, comment: str | None = ''):
        """Уменьшает или увеличивает счетчик тревоги на значение"""
        latest = self.get_last_counter()
        new_value = latest + value if increase else latest - value
        self.set_alert_counter(new_value, comment)

    def set_alert_counter(self, value: int, comment: str | None = 'auto-change by alert service'):
        """Изменяет числовое значение счетчика тревоги"""
        counter = AlertCounter(value, comment)
        counter.save()
        # todo: this is duplicate of check in AlertCounterSerializer, refactor later
        is_new_state = self.get_state_by_alert(value)
        if is_new_state != self.current:
            self.set_state_current(is_new_state)

    @staticmethod
    def get_last_counter() -> int:
        try:
            counter = AlertCounter.objects.latest('id')
        except AlertCounter.DoesNotExist:
            counter = AlertCounter(
                value=0,
                comment='initial counter set by AlertService'
            )
            counter.save()
        return counter.value

    def compare_threshold_by_name(self, level_name: str) -> bool:
        """Сравнивает трешхолд выбранного уровня с трешхолдом текущего"""
        new = AlertState.get_by_name(level_name)
        return new.threshold > self.get_state_current().threshold

    def split_thresholds(self, count: int = 3) -> List[int]:
        range_size = self.max_alert_value - self.min_alert_value
        sub_range_size = range_size / count
        thresholds = []
        threshold = self.min_alert_value
        for _ in range(count):
            threshold += sub_range_size
            thresholds.append(int(threshold))

        return thresholds

    @staticmethod
    def get_state_current() -> AlertState:
        return AlertState.objects.filter(current=True).first()

    @staticmethod
    def set_state_current(instance: AlertState) -> AlertState:
        if not instance.current:
            instance.current = True
            instance.save()
        return instance

    @property
    def max_alert_value(self) -> int:
        states = [state.threshold for state in AlertState.objects.all().order_by("threshold")]
        return max(states) if states else self.min_alert_value

    @staticmethod
    def _get_ingame_states(sort_by: str | None = 'order'):
        """Получает все внутриигровые статусы"""
        return sorted([state.is_ingame for state in AlertState.objects.all()], key=itemgetter(sort_by))

    def _calc_alert_ranges(self):
        """Вычисляет начальные и конечные уровни тревоги для каждого статуса"""
        result = {}
        self.state_ranges = dict()
        self.states = dict(enumerate(self._get_ingame_states()))
        max_scale_value = self.max_alert_value + int(round(self.max_alert_value * 0.1))

        for index, item in self.states.items():
            nxt = self.states.get(index + 1)
            nxt_threshold = getattr(nxt, 'threshold', max_scale_value)
            result.update({index: [item.threshold, nxt_threshold]})
        return result

    def __str__(self):
        return 'AlertService'

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return
