from peripheral_devices.models import LockDevice, SkabenDevice, TerminalDevice
from peripheral_devices.serializers import LockSerializer, TerminalSerializer


def get_model_by_topic(topic: str) -> SkabenDevice:
    table = {"lock": LockDevice, "terminal": TerminalDevice}
    result = table.get(topic)
    if not result:
        raise ValueError(f"cannot find model by topic: {topic}")
    return result


def get_serializer_by_topic(topic: str) -> LockSerializer | TerminalSerializer:
    table = {"lock": LockSerializer, "terminal": TerminalSerializer}
    result = table.get(topic)
    if not result:
        raise ValueError(f"cannot find serializer by topic: {topic}")
    return result
