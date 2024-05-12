from pydantic import ValidationError

from core.transport.events import SkabenEventContext, ContextEventLevels
from event_contexts.device.events import SkabenDeviceEvent
from event_contexts.device.lock_access_context import LockEventContext
from event_contexts.device.power_shield_context import PowerShieldEventContext
from event_contexts.exceptions import StopContextError


class DeviceEventContext(SkabenEventContext):
    context_dispatcher = {
        "lock": LockEventContext,
        "pwr": PowerShieldEventContext,
    }

    def apply(self, event_headers: dict, event_data: dict):
        try:
            event_type = event_headers.get("event_type", "")
            device_type = event_headers.get("device_type", "")
            if not SkabenDeviceEvent.is_mine(event_type):
                return False
            ctx = self.context_dispatcher.get(device_type)
            if not ctx:
                return False
            with ctx() as context:
                result = context.apply(event_headers=event_headers, event_data=event_data)
                self.events = context.events[:]
                return result
        except StopContextError as e:
            self.add_event(message=e.error, level=ContextEventLevels.ERROR)
            return False
        except (ValueError, ValidationError) as e:
            self.add_event(message=str(e), level=ContextEventLevels.ERROR)
            return False
