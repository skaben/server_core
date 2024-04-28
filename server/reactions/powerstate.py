from dataclasses import dataclass

from alert.service import AlertService
from alert.models import AlertState
from reactions.exceptions import StopReactionPipeline


@dataclass(frozen=True)
class PowerShieldStates:
    
    POWER_ON = 'pwr'
    POWER_AUX = 'aux'
    POWER_OFF = 'off'

    @property
    def states(self):
        return [self.POWER_AUX, self.POWER_OFF, self.POWER_ON] 


def apply_powerstate(event_data: dict):
    """Меняет уровень тревоги в зависимости от статуса щитка"""
    command = event_data.get("powerstate")
    device_type = event_data.get("device_type")
    shield = PowerShieldStates()
    if command and device_type and device_type.lower() == "pwr":
        if command not in shield.states:
            raise StopReactionPipeline(f'Powershield command not found in pipeline: `{command}`')

        if command == shield.POWER_OFF:
            # щиток не переключает статус в этом случае
            raise StopReactionPipeline(f'Powershield sent `{shield.POWER_OFF}`, nothing is happen as it should.')

        with AlertService() as service:
            if command == shield.POWER_AUX:
                state = AlertState.objects.filter(name='cyan').get()
                service.set_state_current(state)

            if command == shield.POWER_ON:
                current_counter = service.get_last_counter()
                state = service.get_state_by_alert(current_counter)
                if not state:
                    raise StopReactionPipeline(f"Error occured when setting state by powershield `{shield.POWER_ON}` command")
                service.set_state_current(state)

            raise StopReactionPipeline(f"state changed to {state}")
