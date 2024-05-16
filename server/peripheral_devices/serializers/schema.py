from typing import Dict, List
from pydantic import BaseModel


class BaseDeviceSchema(BaseModel):
    alert: str
    override: bool


class LockDeviceSchema(BaseDeviceSchema):
    sound: bool
    closed: bool
    blocked: bool
    timer: int
    acl: Dict[str, List[int]]


class TerminalDeviceSchema(BaseDeviceSchema):
    powered: bool
    blocked: bool
