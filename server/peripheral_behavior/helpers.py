from peripheral_behavior.models.passive import PassiveConfig
from alert.models import AlertState


def get_passive_config(device_type: str) -> dict:
    config = {}
    current_state = AlertState.objects.filter(current=True).first()
    if current_state:
        try:
            cfg = PassiveConfig.objects.get(topic=device_type, state=current_state)
            config = cfg.config
        except PassiveConfig.DoesNotExist:
            pass
    return config
