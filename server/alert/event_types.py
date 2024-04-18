from dataclasses import dataclass
from typing import Literal, Optional

from core.transport.events import SkabenEvent

ALERT_STATE: str = 'alert_state'
ALERT_COUNTER: str = 'alert_counter'


@dataclass(frozen=True)
class AlertEventTypes:

    ALERT_STATE = ALERT_STATE
    ALERT_COUNTER = ALERT_COUNTER

    @classmethod
    def get_by_type(cls, event_type: str) -> Optional[SkabenEvent]:
        event_map = {
            cls.ALERT_STATE: AlertStateEvent,
            cls.ALERT_COUNTER: AlertCounterEvent,
        }
        return event_map.get(event_type)


class AlertStateEvent(SkabenEvent):

    event_type: str = ALERT_STATE
    counter_reset: bool = True
    state: str


class AlertCounterEvent(SkabenEvent):

    event_type: str = ALERT_COUNTER
    value: int
    change: Literal['increase', 'decrease', 'set']
    comment: Optional[str]
