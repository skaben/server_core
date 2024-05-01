from event_handling.device.lock_access_info import LockEventContext
from event_handling.device.pwr_state_switch import PowerShieldEventContext
from event_handling.events import SkabenEventContext
from event_handling.exceptions import StopReactionPipeline


class DeviceEventContext(SkabenEventContext):
    context_dispatcher = {
        "lock": LockEventContext,
        "pwr": PowerShieldEventContext,
    }

    def apply(self, event_headers: dict, event_data: dict):
        """Базовый пайплайн обработки эвентов"""
        event_type = event_headers.get("event_type", "")
        device_type = event_headers.get("device_type", "")
        try:
            if event_type == "device":
                ctx = self.context_dispatcher.get(device_type)
                if not ctx:
                    raise ValueError(f"cannot find context for handling `{event_headers}` `{event_data}`")
                with ctx() as context:
                    context.apply(event_data)
        except StopReactionPipeline:
            return
