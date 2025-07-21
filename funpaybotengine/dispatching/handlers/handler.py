from __future__ import annotations


__all__ = ('Handler',)

from typing import TYPE_CHECKING, Any, Type
from dataclasses import dataclass
from collections.abc import Callable, Awaitable


if TYPE_CHECKING:
    from funpaybotengine.dispatching.events.base import Event
    from funpaybotengine.dispatching.filters.base import Filter
    from funpaybotengine.dispatching.handlers.handler_manager import HandlerManager


@dataclass
class Handler:
    id: str
    """Handler ID."""

    event_type: Type[Event[Any]]
    """Event type, on which this handler should be executed."""

    filter: Filter | None
    """Handler filter."""

    callable: Callable[[Event[Any], ...], Awaitable[Any]]  # type: ignore[misc]  # expected
    """Original callable."""

    manager: HandlerManager
    """Handler manager to which this handler is bound."""