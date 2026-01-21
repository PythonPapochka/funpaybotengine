from __future__ import annotations


__all__ = ('Event', 'RunnerEvent', 'BotEngineEvent', 'ExceptionEvent')


from typing import Any, Generic, TypeVar

from pydantic import Field
from eventry.asyncio.event import ExtendedEvent

from funpaybotengine.base import BindableObject


EventObject = TypeVar('EventObject')


class Event(ExtendedEvent, BindableObject, Generic[EventObject], name='event'):
    model_config = {
        'arbitrary_types_allowed': True,
    }
    object: EventObject = Field(frozen=True)

    @property
    def event_context_injection(self) -> dict[str, Any]:
        return {'object': self.object}

    def __hash__(self) -> int:
        return id(self)


class RunnerEvent(Event[EventObject], name='runner'):
    tag: str | None = Field(frozen=True)

    @property
    def event_context_injection(self) -> dict[str, Any]:
        injection = super().event_context_injection
        injection['tag'] = self.tag
        return injection


class BotEngineEvent(Event[EventObject], name='funpaybotengine'): ...


class ExceptionEvent(BotEngineEvent[Exception], name='error'):
    event: Event[Any] = Field(frozen=True)

    @property
    def event_context_injection(self) -> dict[str, Any]:
        injection = super().event_context_injection
        injection.update({'on_event': self.event, 'exception': self.object})
        return injection
