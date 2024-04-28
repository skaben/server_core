from reactions.exceptions import StopReactionPipeline
from reactions.powerstate import apply_powerstate
from reactions.access_mgmt import apply_card


def handle(event_headers: dict, event_data: dict):
    """Базовый пайплайн обработки эвентов"""
    event_type = event_headers.get("event_type", "")
    device_type = event_headers.get("device_type", "")
    try:
        if event_type == "device":
            if device_type == "pwr":
                return apply_powerstate(event_data)
            if device_type == "lock":
                apply_card(data=event_data, source=event_headers.get("device_uid", ""))
    except StopReactionPipeline as e:
        print(e)
