import logging
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel as PydanticBaseModel
from pydantic_core import from_json


class BaseModel(PydanticBaseModel):

    class Config:
        arbitrary_types_allowed = True


class EncodedEventType(BaseModel):

    data: Optional[Dict[str, Any]]
    headers: Optional[Dict[str, Any]]


class SkabenEvent(BaseModel):
    """Базовый внутренний эвент.

    Attributes:
    name (str): Наименование события. Будет добавлено в routing_key
    context (bool): Указывает, обработано ли событие.
    """

    event_type: str = "change_me"  # определяет тип сообщения
    event_source: str = "default"  # определяет источник сообщения

    def encode(self) -> EncodedEventType:
        """Подготавливает данные события для отправки во внутреннюю очередь.

        Возвращает тип события для включения в заголовок сообщения очереди и полезную нагрузку события."""
        headers = {
            "event_type": self.event_type,
            "event_source": self.event_source,
        }
        event = EncodedEventType(headers=headers, data=self.model_dump(exclude=["event_type", "event_source"]))
        return event

    @staticmethod
    def decode(event_headers: dict, event_data: Union[str, dict]) -> dict:
        """Подготавливает данные к валидации моделью."""
        if isinstance(event_data, dict):
            _converted_event_data = event_data
        else:
            try:
                _converted_event_data = from_json(event_data)
            except:
                logging.error(event_data)
                logging.error(type(event_data))

        return {
            "event_type": event_headers.get("event_type", ""),
            "event_source": event_headers.get("event_source", ""),
            **_converted_event_data,
        }
