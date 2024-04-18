import logging
from django.conf import settings
from peripheral_behavior.models import AccessCode
from peripheral_devices.models import LockDevice as Lock

# TODO: SHOULD BE REFACTORED ASAP, many things have changed


def apply(data: dict, source: str) -> tuple[bool, str]:
    """
    Трансформирует код в данные обладателя
    или создает новую пустую запись карты если такого пользователя нет
    """
    card_len = settings.ACCESS_CODE_CARD_LEN
    access_code = data.get("peripherals")
    try:
        person = AccessCode.objects.filter(code=access_code).first()
        lock = Lock.objects.filter(addr=source).first()
        success = "доступ разрешен" if data.get("success") else "доступ запрещен"
        return True, f"{lock} : {success} для {person}"
    except AccessCode.DoesNotExist:
        if card_len + 1 > len(str(access_code)) < card_len:
            return False, f"Код не является картой и его нет в базе - {access_code}"
        instance = AccessCode(code=access_code, name=f"{access_code} from {source}")
        instance.save()
        return False, f"WARN: Первая попытка авторизации {instance.code} в {source}"
    except Lock.DoesNotExist:
        logging.error(f"no active lock found for the {source}")
        # todo: call new device init procedure
