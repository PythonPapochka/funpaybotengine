from __future__ import annotations


__all__ = ('Handler',)

from typing import TYPE_CHECKING, Any
from dataclasses import dataclass
from collections.abc import Callable


if TYPE_CHECKING:
    from funpaybotengine.dispatching.events.base import Event
    from funpaybotengine.dispatching.filters.base import Filter


@dataclass
class Handler:
    id: str
    filter: Filter | None
    callable: Callable[[Event[Any], ...], Any]  # type: ignore[misc]  # expected
