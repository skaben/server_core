import time
from actions.scenario.base import BaseScenario
from actions.models import EnergyState
from alert.models import get_current
from core.models import get_system_settings
from actions.alert import AlertServiceExtended
from eventlog.serializers import EventSerializer

"""
1. все незашифрованные тексты + литании управления - в данж под хак (6, таймаут 3 минуты)
2. все зашифрованные тексты - в технолингве - в терминал в шкафу - DONE
note: и там и там - спросить Макса про ротацию текстов по ходу игры...
DONE
---

отдельно консоль и отдельно логи.

отдельно медблок.
работает только если есть энергия на него.

прошивка замков:

входной замок на КПП - пускает вообще всех кроме D
выходной замок (аварийный) - не пускает никого (blocked не в аварии)
замок к Вайфу - пускает всех только А

пустотные поля (подулье) - пускают А и B.
TODO: отключены если не распределена энергия туда

TODO: сделать две люстры на ПодУлей, которые слушают hive

TODO: запилить статусы для щитка
"""



class Scenario(BaseScenario):

    DISPATCH_POWER_TABLE = {
        'AUX': 'reset',
        'PWR': 'reset'
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
            'RUPTURAOMNISPOTENTIA': self.emp_blast,
            'OMNISSIAH': self.omnissiah
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
            "timestamp": int(time.time()) + 3,
            "message": {
                "type": "console",
                "content": message.upper(),
                "response": True
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
        # сообщение пишется при смене статуса
        fail_message = 'Внимание! Система не может быть переведена в аварийный режим!'
        try:
            if self.current.name not in ["error", "reset", "emp"]:
                with AlertServiceExtended() as service:
                    service.set_state_by_name("error")
            else:
                self.write_event(fail_message)
        except Exception:
            self.write_event(fail_message)
            raise

    def emp_blast(self):
        # сообщение пишется при смене статуса
        fail_message = 'Отказано в доступе. Известите МГ.'
        try:
            if self.current.name != "emp":
                with AlertServiceExtended() as service:
                    service.set_state_by_name("emp")
        except Exception:
            self.write_event(fail_message)
            raise

    def energy_has_slots(self):
        """проверяем доступность слотов в текущем цикле"""
        if self.current.name != 'stable':
            return
        energy_state = EnergyState.objects.latest('id')
        slots_used = len(energy_state.load)
        if slots_used < energy_state.slots:
            return energy_state

    def route_energy(self, slot_name, message):
        energy_state = self.energy_has_slots()

        slots_full_message = 'Ошибка распределения. Достигнуто максимальное значение назначенных энергетических контуров в данном цикле.'
        slot_exists_message = f'Ошибка распределения. Для контура {slot_name} энергия уже распределена.'
        not_avail_level = 'В этом состоянии системы распределение невозможно, запустите цикл'

        if not energy_state:
            return self.write_event(not_avail_level)
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
        message = 'Распределена энергия для контура лазарета, запуск авто-дока произведен'
        return self.route_energy(slot_name, message)

    def energy_to_dungeon(self):
        slot_name = "LUMINOS"
        message = 'Распределена энергия для контура закрытых уровней Улья, освещение включено'
        return self.route_energy(slot_name, message)

    def energy_to_gates(self):
        slot_name = "OSTIUM"
        message = 'Распределена энергия для контура питания ворот. Внимание! Ворота теперь могут быть открыты'
        return self.route_energy(slot_name, message)

    def energy_to_production(self):
        slot_name = "FABRICA"
        message = 'Распределена энергия для контура сборочных конвейеров'
        return self.route_energy(slot_name, message)

    def energy_to_radio(self):
        slot_name = "CONNEXUS"
        message = 'Распределена энергия для контура дальней радиосвязи'
        return self.route_energy(slot_name, message)

    def energy_to_navs(self):
        slot_name = "NAVIS"
        message = 'Распределена энергия для контура освещения посадочной площадки'
        return self.route_energy(slot_name, message)

    def omnissiah(self):
        message = (
            'From the moment I understood the weakness of my flesh, it disgusted me. '
            'I craved the strength and certainty of steel. I aspired to the purity of the Blessed Machine. '
            'Your kind cling to your flesh, as if it will not decay and fail you. '
            'One day the crude biomass that you call a temple will wither, and you will beg my kind to save you. '
            'But I am already saved, for the Machine is immortal...'
        )
        self.write_event(message)
        time.sleep(.5)
        self.write_event('...even in death I serve the Omnissiah.')
