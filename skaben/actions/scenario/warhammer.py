import time
from actions.scenario.base import BaseScenario
from actions.models import EnergyState
from alert.models import get_current
from core.models import get_system_settings
from actions.alert import AlertService
from actions.device import update_terminals, update_locks
from eventlog.serializers import EventSerializer


LOCK_MAIN_UUID = '12425412b519'
LOCK_BACK_UUID = '12425412b511'


class AlertServiceExtended(AlertService):

    def set_state_current(self, instance):
        backup = get_current()
        try:
            alert_state = super().set_state_current(instance)
            critical_states = [
                'emp',
                'error'
            ]
            if alert_state.name in critical_states:
                if alert_state.name == "emp":
                    update_terminals({"powered": False})
                    update_locks({"closed": False, "blocked": True})
                if alert_state.name == "error":
                    update_terminals({"blocked": True})
                    update_locks({"closed": True, "blocked": True})
                    update_locks({"blocked": False}, uid=LOCK_BACK_UUID)
            else:
                update_terminals({"blocked": False, "powered": True})
                update_locks({"closed": True, "blocked": False})
                update_locks({"blocked": True}, uid=LOCK_BACK_UUID)
        except Exception:
            # rollback
            super().set_state_current(backup)
            raise


class Scenario(BaseScenario):

    DISPATCH_POWER_TABLE = {
        'AUX': 'reset',
        'PWR': 'static'
    }

    def __init__(self):
        self.current = None
        self.energy_state = None
        self.device_type = ''
        self.device_uid = ''
        self.COMMANDS = {
            'IGNITIOMOBILIOMNIS': self.cycle_start,
            'INCIPEREMODUSMEDICA': self.energy_to_medic,
            'INCIPEREMODUSLUMINOS': self.energy_to_dungeon,
            'INCIPEREMODUSOSTIUM': self.energy_to_gates,
            'INCIPEREMODUSFABRICA': self.energy_to_production,
            'INCIPEREMODUSCONNEXUS': self.energy_to_radio,
            'INCIPEREMODUSNAVIS': self.energy_to_navs,
            'EXITUSTEMPUSMOBILI': self.cycle_end,
            'EXITUSMODUSEXTREMITAS': self.cycle_restore,
            'EXTREMITASMODUSADIGO': self.cycle_break,
            'RUPTURAOMNISPOTENTIA': self.emp_blast
        }

    def pipeline(self, data: dict):
        self.device_type = data.get('device_type')
        self.device_uid = data.get('device_uid')
        self.datahold = data.get('datahold')
        self.current = get_current()

        if self.device_type == 'pwr':
            return self.check_power_state(self.datahold.get('powerstate'))

        if self.device_type == 'terminal':
            # обеспечиваем выполнение команд управляющей консоли
            if self.datahold.get('type') == 'input':
                if self.current.name == "config":
                    return self.write_event('СИСТЕМА В РЕЖИМЕ КОНФИГУРАЦИИ, ИЗМЕНИТЕ СТАТУС')
                command = self.COMMANDS.get(self.datahold.get('content', 'empty'))
                if command:
                    return command()

    def write_event(self, message: str):
        """Записываем событие для отображения в терминале"""
        event_data = {
            "level": "info",
            "stream": self.device_type,
            "source": self.device_uid,
            "timestamp": int(time.time()) + 1,
            "message": {
                "type": "console",
                "content": message.upper()
            }
        }
        serializer = EventSerializer(data=event_data)
        if serializer.is_valid():
            serializer.save()

    def cycle_start(self):
        ok_message = 'Запуск цикла инициирован, ожидается распределение энергии'
        fail_message = 'Цикл не может быть запущен из этого состояния'
        try:
            if self.current.name == "static":
                slots = get_system_settings().energy_slots
                energy_state = EnergyState(slots=slots)
                energy_state.save()
                with AlertServiceExtended() as service:
                    service.set_state_by_name("stable")
                self.write_event(ok_message)
            else:
                self.write_event(fail_message)
        except Exception:
            self.write_event(fail_message)
            raise

    def cycle_end(self):
        ok_message = 'Цикл завершен. Система перешла в режим ожидания'
        fail_message = 'Цикл не может быть завершен в этом состоянии'
        try:
            if self.current.name == "stable":
                with AlertServiceExtended() as service:
                    service.set_state_by_name("static")
                self.write_event(ok_message)
            else:
                self.write_event(fail_message)
        except Exception:
            self.write_event(fail_message)
            raise

    def cycle_restore(self):
        ok_message = 'Система успешно переведена в режим ожидания и готова к новому циклу'
        fail_message = 'Система не может быть переведена в рабочий режим.'
        try:
            if self.current.name == "reset":
                with AlertServiceExtended() as service:
                    service.set_state_by_name("static")
                self.write_event(ok_message)
            else:
                self.write_event(fail_message)
        except Exception:
            self.write_event(fail_message)
            raise

    def cycle_break(self):
        ok_message = 'Внимание! Система перешла в аварийный режим! Внимание!'
        fail_message = 'Внимание! Система не может быть переведена в аварийный режим!'
        try:
            if self.current.name not in ["error", "reset", "emp"]:
                with AlertServiceExtended() as service:
                    service.set_state_by_name("error")
                self.write_event(ok_message)
            else:
                self.write_event(fail_message)
        except Exception:
            self.write_event(fail_message)
            raise

    def emp_blast(self):
        ok_message = 'Внимание! Перегрузка внешнего контура! Активирован протокол защиты от EMP-удара.'
        if self.current.name != "emp":
            with AlertServiceExtended() as service:
                service.set_state_by_name("emp")
            self.write_event(ok_message)

    @staticmethod
    def energy_has_slots():
        """проверяем доступность слотов в текущем цикле"""
        energy_state = EnergyState.objects.latest('id')
        slots_used = len(energy_state.load)
        if slots_used < energy_state.slots:
            return energy_state

    def route_energy(self, slot_name, message):
        energy_state = self.energy_has_slots()
        slots_full_message = 'Ошибка распределения. Достигнуто максимальное значение назначенных энергетических контуров в данном цикле.'
        slot_exists_message = f'Ошибка распределения. Для контура {slot_name} энергия уже распределена.'
        if not energy_state:
            return self.write_event(slots_full_message)
        elif energy_state.load.get(slot_name):
            return self.write_event(slot_exists_message)
        else:
            energy_state.load = {
                slot_name: True,
                **energy_state.load
            }
            energy_state.save()
            return self.write_event(message)

    def energy_to_medic(self):
        slot_name = "MEDICA"
        message = 'Распределена энергия для лазарета, запуск авто-дока произведен'
        return self.route_energy(slot_name, message)

    def energy_to_dungeon(self):
        slot_name = "LUMINOS"
        message = 'Распределена энергия для закрытых уровней Улья, освещение включено'
        return self.route_energy(slot_name, message)

    def energy_to_gates(self):
        slot_name = "OSTIUM"
        message = 'Распределена энергия для питания ворот. Внимание! Ворота теперь могут быть открыты'
        return self.route_energy(slot_name, message)

    def energy_to_production(self):
        slot_name = "FABRICA"
        message = 'Распределена энергия на нужды сборочных конвейеров'
        return self.route_energy(slot_name, message)

    def energy_to_radio(self):
        slot_name = "CONNEXUS"
        message = 'Распределена энергия на нужды радио-связи'
        return self.route_energy(slot_name, message)

    def energy_to_navs(self):
        slot_name = "NAVIS"
        message = 'Распределена энергия для освещения посадочной площадки'
        return self.route_energy(slot_name, message)
