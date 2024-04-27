from alert.service import AlertService
from django.conf import settings
from reactions.exceptions import StopReactionPipeline

dispatch = settings.PWR_STATE_DISPATCH_TABLE


def apply_powerstate(event_data: dict):
    """Меняет уровень тревоги в зависимости от статуса щитка"""
    command = event_data.get("powerstate")
    device_type = event_data.get("device_type")
    if command and device_type and device_type.lower() == "pwr":
        name = dispatch.get(command.lower())
        if not name:
            raise StopReactionPipeline(
                f"state not found: {command.lower()} not found in available state names: {dispatch.keys()}"
            )
        with AlertService() as service:
            current = service.get_state_current()
            if current.name != name:
                service.set_state_by_name(name)
                raise StopReactionPipeline(f"state changed to {name}")
