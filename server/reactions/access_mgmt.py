from typing import Tuple

from django.conf import settings
from peripheral_behavior.models import AccessCode
from peripheral_devices.models import LockDevice as Lock


def _close_lock(lock: Lock, close: bool):
    """Закрывает замок с отправкой апдейта."""
    if lock.closed != close:
        lock.closed = close
        lock.save(send_update=True)


def apply_card(data: dict, source: str) -> Tuple[bool, str]:
    """Применяет правила открытия замка ключ-картой или кодом."""
    card_len = settings.ACCESS_CODE_CARD_LEN
    access_code = data.get("peripherals") # ???

    try:
        lock = Lock.objects.filter(mac_addr=source).get()
        access = AccessCode.objects.filter(code=access_code).get()
        if data.get("success"):
            _close_lock(lock, False)
        else:
            _close_lock(lock, True)

        success = "доступ разрешен" if data.get("success") else "доступ запрещен"
        return True, f"{lock} : {success} для {access}"

    except AccessCode.DoesNotExist:
        if card_len + 1 > len(str(access_code)) < card_len:
            _close_lock(lock, True)
            return False, f"Код не является картой и его нет в базе - {access_code}"
        instance = AccessCode(code=access_code, name=f"{access_code} from {source}")
        instance.save()
        return False, f"Первая попытка авторизации {instance.code} в {source}"

    except Lock.DoesNotExist:
        new_lock = Lock.objects.create(mac_addr=source)
        new_lock.save()
        return False, f'Создано новое устройство типа `Замок` с адресом {source}'
