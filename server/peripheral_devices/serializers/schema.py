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
    permissions: Dict[str, List[int]]
