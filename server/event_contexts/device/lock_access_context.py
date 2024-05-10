from alert.models import AlertState
from django.conf import settings
from core.transport.events import SkabenEventContext, ContextEventLevels
from event_contexts.exceptions import StopContextError
from peripheral_behavior.models import AccessCode
from peripheral_devices.models import LockDevice as Lock


class LockEventContext(SkabenEventContext):
    """Контекст обработки событий от лазерных дверей.

    Создает сообщения об открытии\закрытии\блокировке.
    В maintenance-режиме работы среды (white) - позволяет добавлять неизвестные системе карточки.
    """

    @staticmethod
    def create_lock_device(mac_addr: str) -> str:
        """Создает новое устройство типа 'Лазерная дверь'."""
        mgmt_state = AlertState.objects.get_management_state()
        if not mgmt_state.current:
            return "Устройство не зарегистрировано и должно быть создано в режиме управления средой (white)."

        new_lock = Lock.objects.create(mac_addr=mac_addr)
        new_lock.save()
        return f"Создано новое устройство типа `Замок` с адресом {mac_addr}"

    @staticmethod
    def create_new_access_record(lock_name: str, access_code: str) -> str:
        if str(access_code) != settings.ACCESS_CODE_CARD_LEN:
            raise StopContextError(f"Код не является картой и его нет в базе - {access_code}")
        mgmt_state = AlertState.objects.get_management_state()
        if not mgmt_state.current:
            raise StopContextError(
                f"Первая попытка авторизации {access_code} в {lock_name} -> не может быть добавлен (white статус не активен)."
            )

        instance = AccessCode(code=access_code, name=f"AUTO: {access_code} from {lock_name}")
        instance.save()
        return f"Первая попытка авторизации {instance.code} в {lock_name} -> {instance.code} добавлен в БД."

    def apply(self, event_headers: dict, event_data: dict):
        """Применяет правила открытия замка ключ-картой или кодом."""
        source = event_headers.get("device_uid", "")
        access_code = event_data.get("access_code", "")

        try:
            lock = Lock.objects.filter(mac_addr=source).get()
            access = AccessCode.objects.filter(code=access_code).get()
            success = event_data.get("success")
            result = "доступ разрешен" if success else "доступ запрещен"
            self.add_event(f"{lock.id} : {result} для {access}")

        except AccessCode.DoesNotExist:
            lock = Lock.objects.filter(mac_addr=source).get()
            message = self.create_new_access_record(lock_name=lock.description[:30], access_code=access_code)
            self.add_event(message, level=ContextEventLevels.LOG)
        except Lock.DoesNotExist:
            message = self.create_lock_device(mac_addr=source)
            self.add_event(message, level=ContextEventLevels.LOG)
