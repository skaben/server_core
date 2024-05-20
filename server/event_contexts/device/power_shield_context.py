from dataclasses import dataclass

from alert.models import AlertState
from alert.service import AlertService
from core.transport.events import SkabenEventContext
from event_contexts.exceptions import StopContextError


@dataclass(frozen=True)
class PowerShieldStates:
    POWER_ON = "pwr"
    POWER_AUX = "aux"
    POWER_OFF = "off"

    @property
    def states(self):
        return [self.POWER_AUX, self.POWER_OFF, self.POWER_ON]


class PowerShieldEventContext(SkabenEventContext):
    """Контекст обработки сообщений от силового щитка.

    На этом устройстве работает механизм запуска игровой среды.
    Переключает уровни тревоги из предварительных в игровые в результате решения квеста игроками.
    """

    def apply(self, event_headers: dict, event_data: dict):
        """Меняет уровень тревоги в зависимости от команды щитка."""
        command = event_data.get("powerstate", "").lower()
        device_type = event_headers.get("device_type")

        if command and device_type and device_type.lower() == "pwr":
            shield = PowerShieldStates()

            if command not in shield.states:
                raise StopContextError(f"Powershield command not found in pipeline: `{command}`")

            if command == shield.POWER_OFF:
                # щиток не переключает статус в этом случае
                return

            with AlertService() as service:
                if command == shield.POWER_AUX:
                    pre_ignition_state = AlertState.objects.is_pre_ignition_state()
                    # щиток переключает статус только из полностью выключенного режима
                    if pre_ignition_state:
                        state = AlertState.objects.get(name="cyan")
                        service.set_state_current(state)
                elif command == shield.POWER_ON:
                    # щиток переключает режим в первый игровой статус
                    pre_power_state = AlertState.objects.is_pre_power_state()
                    if pre_power_state:
                        state = service.get_ingame_states(sort_by="order").first()
                        if not state:
                            raise StopContextError(
                                f"Error occured when setting state by powershield `{shield.POWER_ON}` command"
                            )
                        service.set_state_current(state)
