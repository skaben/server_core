from typing import Optional, Dict, List
from pydantic import ValidationError, field_validator

from core.transport.topics import SkabenTopics
from core.transport.events import SkabenEvent


class SkabenDeviceEvent(SkabenEvent):
    """Событие периферийного устройства.

    Эти события сообщают об изменениях внутреннего состояния устройств и о взаимодействии пользователей с ними.
    """

    event_type: str = "device"
    device_type: str
    device_uid: Optional[str]
    payload: Optional[Dict[str, any]] = {}

    @property
    def headers(self) -> List[str]:
        return super().headers + ["device_type", "device_uid"]

    @field_validator("device_type")
    def validate_device_type(cls, v):
        topics = SkabenTopics()
        if v not in topics.all:  # todo: get from DeviceTopics model
            raise ValidationError(f"Invalid topic. Allowed values are: {topics.all}")
        return v
