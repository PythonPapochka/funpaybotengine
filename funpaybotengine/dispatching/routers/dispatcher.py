from __future__ import annotations


__all__ = ('Dispatcher',)


from typing import TYPE_CHECKING, Any
from funpaybotengine.dispatching.routers.base import Router

if TYPE_CHECKING:
    from funpaybotengine.dispatching.events.base import Event
    from funpaybotengine.dispatching.handlers.handler import Handler


class Dispatcher(Router):
    def __init__(self) -> None:
        super().__init__(
            id='dispatcher'
        )

    async def propagate_event(self, event: Event[Any]) -> None:
        async for handler in self.get_matching_handlers(event):
            await self.execute_handler(event, handler)

    async def execute_handler(self, event: Event[Any], handler: Handler) -> None:
        await handler.callable(event)
