from typing import Optional

import time

from eventlog.serializers import EventSerializer
from .device import send_config_to_simple, update_terminals, update_locks
from alert.models import (
    AlertCounter,
    AlertState,
    get_max_alert_value,
    get_ingame_states,
    get_current
)

from django.core.exceptions import ObjectDoesNotExist


LOCK_MAIN_UUID = '12422a54dcf4'
LOCK_BACK_UUID = '1242cb2129e4'
KONSOLE_UUID = 'c0188576509d'
GATE_LOCK_UUID = '124205d2ad79'
LOCK_CORE = '124255f5c920'


class AlertService:
    """ Global Alert State service """

    def __init__(self):
        self.state_ranges = dict()
        self._min_val = 1
        self._max_val = get_max_alert_value()
        self.states = dict(enumerate(get_ingame_states()))
        max_scale_value = self._max_val + int(round(self._max_val * 0.1))

        for index, item in self.states.items():
            next = self.states.get(index + 1)
            next_threshold = getattr(next, 'threshold', max_scale_value)
            self.state_ranges.update({index: [item.threshold, next_threshold]})

    def get_state_by_name(self, name: str):
        return AlertState.objects.filter(name=name).first()

    def get_state_by_alert(self, alert_value: int):
        try:
            alert_value = int(alert_value)
            for index, _range in self.state_ranges.items():
                if alert_value in range(*_range):
                    return self.states.get(index)
        except Exception:
            raise

    def set_state_by_name(self, name: str):
        try:
            instance = AlertState.objects.filter(name=name).first()
            self.set_state_current(instance)
        except ObjectDoesNotExist:
            raise

    def change_alert_level(self,
                           increase: Optional[bool] = True,
                           value: Optional[int] = None) -> AlertCounter:
        try:
            latest = AlertCounter.objects.latest('id').value
        except:
            latest = 0

        current = get_current()
        if not value:
            value = latest + current.modifier
        if not increase:
            value = latest - current.modifier

        counter = AlertCounter(value=value)
        counter.save()

        is_new_state = self.get_state_by_alert(value)
        if is_new_state != current:
            self.set_state_current(is_new_state)

    @staticmethod
    def reset_counter_to_threshold(instance):
        data = {
            'value': instance.threshold,
            'comment': f'changed to {instance.name} by API call'
        }
        return data

    @staticmethod
    def set_state_current(instance: AlertState) -> AlertState:
        try:
            if not instance.current:
                instance.current = True
                instance.save()
                # send_config_all()  # DEPRECATED после внедрения механизма хэша для умных
                send_config_to_simple()
        except ObjectDoesNotExist:
            pass
        finally:
            return instance

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return


def write_event(stream: str, source: str, message: str):
    """Записываем событие для отображения в терминале"""
    event_data = {
        "level": "info",
        "stream": stream,
        "source": source,
        "timestamp": int(time.time()) + 1,
        "message": {
            "type": "console",
            "content": message.upper(),
            "response": True
        }
    }
    serializer = EventSerializer(data=event_data)
    if serializer.is_valid():
        serializer.save()


class AlertServiceExtended(AlertService):

    """Warhammer version"""

    def set_state_current(self, instance):
        backup = get_current()
        try:
            alert_state = super().set_state_current(instance)
            critical_states = [
                'emp',
                'error',
                'reset'
            ]
            if alert_state.name in critical_states:
                if alert_state.name == "emp":
                    update_terminals({"powered": False})
                    update_locks({"closed": False, "blocked": True})
                    write_event("terminal", KONSOLE_UUID,
                                'Внимание! Перегрузка внешнего контура! Активирован протокол защиты от EMP-удара.')
                if alert_state.name == "error":
                    update_terminals({"blocked": True})
                    update_locks({"closed": True, "blocked": True})
                    update_locks({"closed": False}, uid=LOCK_BACK_UUID)
                    write_event("terminal", KONSOLE_UUID, 'Внимание! Система перешла в аварийный режим! Внимание!')
                if alert_state.name == "reset":
                    write_event("terminal", KONSOLE_UUID, 'Внимание! Система перешла в режим восстановления.')
                    update_locks({"blocked": True, "closed": False}, uid=LOCK_CORE)
                    update_locks({"blocked": True, "closed": False}, uid=LOCK_BACK_UUID)
            else:
                update_terminals({"blocked": False, "powered": True})
                update_locks({"closed": True, "blocked": False})
                update_locks({"blocked": True}, uid=LOCK_BACK_UUID)
        except Exception:
            # rollback
            super().set_state_current(backup)
            raise
