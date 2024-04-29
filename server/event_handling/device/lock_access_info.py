from typing import Tuple

from alert.models import AlertState
from django.conf import settings
from peripheral_behavior.models import AccessCode
from peripheral_devices.models import LockDevice as Lock


class LockEventContext:

    def create_lock_device(self, mac_addr: str) -> str:
        mgmt_state = AlertState.objects.get_management_state()
        if not mgmt_state.current:
            return "Устройство не зарегистрировано и должно быть создано в режиме управления средой (white)."

        new_lock = Lock.objects.create(mac_addr=mac_addr)
        new_lock.save()
        return f"Создано новое устройство типа `Замок` с адресом {mac_addr}"

    def create_new_access_record(self, lock_name: str, access_code: str) -> str:
        card_len = settings.ACCESS_CODE_CARD_LEN
        if card_len + 1 > len(str(access_code)) < card_len:
            return f"Код не является картой и его нет в базе - {access_code}"
        mgmt_state = AlertState.objects.get_management_state()
        if not mgmt_state.current:
            return f"Первая попытка авторизации {access_code} в {lock_name} -> не может быть добавлен (white статус не активен)."

        instance = AccessCode(code=access_code, name=f"AUTO: {access_code} from {lock_name}")
        instance.save()
        return f"Первая попытка авторизации {instance.code} в {lock_name} -> {instance.code} добавлен в БД."

    def apply(self, event_data: dict):
        """Применяет правила открытия замка ключ-картой или кодом."""
        result_message = ""
        source = event_data.get("device_uid", "")
        access_code = event_data.get("access_code", "")

        try:
            lock = Lock.objects.filter(mac_addr=source).get()
            access = AccessCode.objects.filter(code=access_code).get()
            success = "доступ разрешен" if event_data.get("success") else "доступ запрещен"
            result_message = f"{lock} : {success} для {access}"

        except AccessCode.DoesNotExist:
            lock = Lock.objects.filter(mac_addr=source).get()
            result_message = self.create_new_access_record(lock_name=lock.description[:30], access_code=access_code)
        except Lock.DoesNotExist:
            result_message = self.create_lock_device(mac_addr=source)
        finally:
            print(result_message)
