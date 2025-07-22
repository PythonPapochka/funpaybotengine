from __future__ import annotations


__all__ = ('Handler',)

from typing import TYPE_CHECKING, Any, Type, Concatenate, ParamSpec
from dataclasses import dataclass
from collections.abc import Callable, Awaitable


if TYPE_CHECKING:
    from funpaybotengine.dispatching.events.base import Event
    from funpaybotengine.dispatching.filters.base import Filter
    from funpaybotengine.dispatching.handlers.handler_manager import HandlerManager, HandlerCallable


@dataclass
class Handler:
    id: str
    """Handler ID."""

    event_type_filter: Type[Event[Any]] | None
    """Event type on which this handler should be executed."""

    filter: Filter | None
    """Handler filter."""

    callable: HandlerCallable[Any, Any, Any]
    """Original callable."""

    manager: HandlerManager[Any]
    """Handler manager to which this handler is bound."""