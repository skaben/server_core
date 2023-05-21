from peripheral_behavior.models.passive import PassiveConfig
# from alert.models import AlertState, AlertCounter
from alert.service import AlertService


def get_passive_config(device_type: str) -> dict:
    config = {}
    with AlertService() as service:
        current = service.get_state_current()
        if not current:
            return config
        try:
            if device_type == 'scl':  # cоздаем конфиг для шкал
                counter = service.get_last_counter()
                config = {
                    "level": counter,
                    "state": current.name,
                    "borders": service.split_thresholds(),
                }
            else:
                cfg = PassiveConfig.objects.get(topic=device_type, state=current.name)
                config = cfg.config
        except PassiveConfig.DoesNotExist:
            pass
    return config
