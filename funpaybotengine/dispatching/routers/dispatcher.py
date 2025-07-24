from __future__ import annotations


__all__ = ('Dispatcher',)


from typing import TYPE_CHECKING, Any

from funpaybotengine.dispatching.events.base import ExceptionEvent
from funpaybotengine.dispatching.routers.base import Router


if TYPE_CHECKING:
    from funpaybotengine.dispatching.bases import HandlerInfo
    from funpaybotengine.dispatching.events.base import Event


class Dispatcher(Router):
    def __init__(self, workflow_data: dict[str, Any] | None = None) -> None:
        super().__init__(name='dispatcher')

        self._workflow_data = workflow_data or {}

    async def propagate_event(self, event: Event[Any]) -> None:
        async for handler in self.get_matching_handlers(event, workflow_data=self._workflow_data):
            await self.execute_handler(event, handler)

    async def execute_handler(self, event: Event[Any], handler: HandlerInfo) -> None:
        workflow_data = {
            **self._workflow_data,
            'event': event,
            'dispatcher': self,
            'handler_info': handler,
        }

        try:
            await handler(**workflow_data)
        except Exception as e:
            event = ExceptionEvent(obj=event, exception=e)
            ...  # todo
