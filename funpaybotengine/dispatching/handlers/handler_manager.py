from __future__ import annotations


__all__ = ('HandlerManager',)

from typing import TYPE_CHECKING, Any, Type

from eventry.asyncio.default_types import FilterType, HandlerType, MiddlewareType
from eventry.asyncio.handler_manager import (
    HandlerManager as BaseHandlerManager,
    MiddlewareManagerTypes,
)
from eventry.asyncio.middleware_manager import MiddlewareManager

from funpaybotengine.dispatching.events.base import Event


if TYPE_CHECKING:
    from funpaybotengine.dispatching.routers import Router


class HandlerManager(BaseHandlerManager[FilterType, HandlerType, MiddlewareType, 'Router']):
    def __init__(
        self,
        router: 'Router',
        handler_manager_id: str,
        event_type_filter: Type[Event[Any]] | None,
    ):
        super().__init__(
            router=router,
            handler_manager_id=handler_manager_id,
            event_type_filter=event_type_filter,
        )

        self._add_middleware_manager(MiddlewareManagerTypes.OUTER, MiddlewareManager())
        self._add_middleware_manager(MiddlewareManagerTypes.INNER, MiddlewareManager())

    @property
    def inner_middleware(self) -> MiddlewareManager:
        return self.middleware_manager(MiddlewareManagerTypes.INNER)  # type: ignore  # not None

    @property
    def outer_middleware(self) -> MiddlewareManager:
        return self.middleware_manager(MiddlewareManagerTypes.OUTER)  # type: ignore  # not None
