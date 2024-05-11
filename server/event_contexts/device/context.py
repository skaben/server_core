from core.transport.events import SkabenEventContext, ContextEventLevels

from event_contexts.device.lock_access_context import LockEventContext
from event_contexts.device.power_shield_context import PowerShieldEventContext
from event_contexts.exceptions import StopContextError


class DeviceEventContext(SkabenEventContext):
    context_dispatcher = {
        "lock": LockEventContext,
        "pwr": PowerShieldEventContext,
    }

    def apply(self, event_headers: dict, event_data: dict):
        event_type = event_headers.get("event_type", "")
        device_type = event_headers.get("device_type", "")
        try:
            if event_type == "device":
                context_specific = self.context_dispatcher.get(device_type)
                if context_specific:
                    with context_specific() as context:
                        context.apply(event_headers=event_headers, event_data=event_data)
                        self.events = context.events[:]
        except StopContextError as e:
            self.add_event(message=e.error, level=ContextEventLevels.ERROR)
        except ValueError as e:
            self.add_event(message=str(e), level=ContextEventLevels.ERROR)
