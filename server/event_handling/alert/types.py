from typing import Literal, Optional

from event_handling.events import SkabenEvent

ALERT_STATE: str = "alert_state"
ALERT_COUNTER: str = "alert_counter"


class AlertStateEvent(SkabenEvent):

    event_type: str = ALERT_STATE
    counter_reset: bool = True
    state: str


class AlertCounterEvent(SkabenEvent):

    event_type: str = ALERT_COUNTER
    value: int
    change: Literal["increase", "decrease", "set"]
    comment: Optional[str]
