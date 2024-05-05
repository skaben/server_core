from typing import Any, Dict, Optional, Union, List, Literal

from dataclasses import dataclass

from pydantic import BaseModel as PydanticBaseModel
from pydantic_core import from_json


class BaseModel(PydanticBaseModel):
    class Config:
        arbitrary_types_allowed = True


class EncodedEvent(BaseModel):
    """Событие, готовое к отправке во внутреннюю очередь."""

    headers: Optional[Dict[str, str | int | bool]]
    data: Optional[Dict[str, Any]]


class SkabenEvent(BaseModel):
    """Базовый внутренний эвент (событие).

    Определяет структуру для различных событий, происходящих внутри приложения (очередь internal).

    Атрибуты:
        event_type (str): Тип события. В соответствии с ним выполняется обработка события роутером.
        event_source (str): Источник события. Это указывает на систему или компонент, который сгенерировал событие. Значение по умолчанию: "default"
        message (str): Дополнительное сообщение, связанное с событием.
        save (bool): Определяет, нужно ли сохранить сообщение в БД.
    """

    event_type: str = "change_me"
    event_source: str = "default"

    def encode(self) -> EncodedEvent:
        """Подготавливает данные события для отправки во внутреннюю очередь.

        Возвращает тип события для включения в заголовок сообщения очереди и полезную нагрузку события."""
        headers_data = {key: getattr(self, key) for key in self.headers}
        event = EncodedEvent(headers=headers_data, data=self.model_dump(exclude={*self.headers}))
        return event

    @property
    def headers(self) -> List[str]:
        """Возвращает список заголовков события."""
        return ["event_type", "event_source"]

    @staticmethod
    def decode(event_headers: dict, event_data: Union[str, dict]) -> dict:
        """Подготавливает данные к валидации моделью."""
        if isinstance(event_data, dict):
            _converted_event_data = event_data
        else:
            _converted_event_data = from_json(event_data)

        return {
            "event_type": event_headers.get("event_type", ""),
            "event_source": event_headers.get("event_source", ""),
            **_converted_event_data,
        }


@dataclass(frozen=True)
class ContextEventLevels:
    LOG: Literal["log"] = "log"
    ERROR: Literal["error"] = "error"
    INFO: Literal["info"] = "info"


class InternalLogEvent(SkabenEvent):
    """Событие внутри контекста, требующее логирования."""

    event_type: str = "log"
    level: Literal["error", "log", "info"] = ContextEventLevels.INFO
    message: str
    message_data: Optional[Dict[str, Any]]
    save: bool = True

    @property
    def headers(self) -> List[str]:
        return super().headers + ["level"]

    def __str__(self):
        return f"[{self.level}] save: {self.save} | {self.message}"


class SkabenEventContext:
    """Базовый контекст обработчика событий."""

    events: List[SkabenEvent] = []

    def apply(self, event_headers: dict, event_data: dict):
        raise NotImplementedError("abstract class method")

    def add_event(
        self,
        message: str,
        level: Literal["error", "log", "info"] = ContextEventLevels.INFO,
        message_data: Optional[Dict[str, Any]] = None,
    ) -> List[SkabenEvent]:
        event = InternalLogEvent(
            message=message,
            message_data=message_data,
            event_source=self._get_context_name(),
            level=level,
        )
        self.events.append(event)
        return self.events

    def _get_context_name(self) -> str:
        return type(self).__name__.lower()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return
