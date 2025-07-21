from __future__ import annotations


__all__ = ('Handler',)

from typing import TYPE_CHECKING, Any, Type
from dataclasses import dataclass
from collections.abc import Callable, Awaitable


if TYPE_CHECKING:
    from funpaybotengine.dispatching.events.base import Event
    from funpaybotengine.dispatching.filters.base import Filter


@dataclass
class Handler:
    id: str
    event_type: Type[Event[Any]]
    filter: Filter | None
    callable: Callable[[Event[Any], ...], Awaitable[Any]]  # type: ignore[misc]  # expected
