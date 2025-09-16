from __future__ import annotations


__all__ = ('Event', 'RunnerEvent', 'BotEngineEvent', 'ExceptionEvent')


from typing import Any, Generic, TypeVar

from pydantic import Field

from funpaybotengine.base import BindableObject
from eventry.asyncio.event import ExtendedEvent


EventObject = TypeVar('EventObject')


class Event(BindableObject, ExtendedEvent, Generic[EventObject]):
    model_config = {
        'arbitrary_types_allowed': True,
    }
    object: EventObject = Field(frozen=True)


class RunnerEvent(Event[EventObject]):
    tag: str = Field(frozen=True)



class BotEngineEvent(Event[EventObject]): ...


class ExceptionEvent(BotEngineEvent[Exception]):
    event: Event[Any] = Field(frozen=True)
    exception: Exception = Field(frozen=True)
