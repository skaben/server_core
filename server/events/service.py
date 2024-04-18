from core.helpers import get_server_timestamp
from events.serializers import EventSerializer


def write_event(stream: str, source: str, _type: str, message: str, level: str = "info"):
    """Записываем событие для отображения в потоке"""

    event_data = {
        "level": level,
        "stream": stream,
        "source": source,
        "timestamp": get_server_timestamp() + 1,  # fixing confusing 'too fast replies'
        "message": {"type": _type, "peripherals": message, "response": True},
    }
    serializer = EventSerializer(data=event_data)
    if serializer.is_valid():
        serializer.save()
