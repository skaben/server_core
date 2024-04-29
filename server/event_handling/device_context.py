from event_handling.exceptions import StopReactionPipeline
from event_handling.pwr_state_switch import PowerShieldEventContext
from event_handling.lock_access_info import LockEventContext


device_context_dispatcher = {
    "lock": LockEventContext,
    "pwr": PowerShieldEventContext,
}


def apply(event_headers: dict, event_data: dict):
    """Базовый пайплайн обработки эвентов"""
    event_type = event_headers.get("event_type", "")
    device_type = event_headers.get("device_type", "")
    try:
        if event_type == "device":
            ctx = device_context_dispatcher.get(device_type)
            if not ctx:
                raise ValueError(f'cannot find context for handling `{event_headers}` `{event_data}`')
            with ctx() as context:
                context.apply(event_data)
    except StopReactionPipeline as e:
        return
