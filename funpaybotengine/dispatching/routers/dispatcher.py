from __future__ import annotations


__all__ = ('Dispatcher',)


from typing import TYPE_CHECKING, Any

from funpaybotengine.dispatching.bases import MiddlewareCallableType, WrappedWithMiddlewaresType
from funpaybotengine.dispatching.events.base import ExceptionEvent
from funpaybotengine.dispatching.middlewares import MiddlewareManager
from funpaybotengine.dispatching.routers.base import Router


if TYPE_CHECKING:
    from funpaybotengine.dispatching.bases import HandlerInfo
    from funpaybotengine.dispatching.events.base import Event


class Dispatcher(Router):
    def __init__(self, workflow_data: dict[str, Any] | None = None) -> None:
        super().__init__(name='dispatcher')

        self._workflow_data = workflow_data or {}

    async def propagate_event(self, event: Event[Any]) -> None:
        workflow_data = {
            **self._workflow_data,
            'event': event,
            'dispatcher': self,
        }

        async for handler in self.get_matching_handlers(event, workflow_data=workflow_data):
            await self.execute_handler(event, handler, workflow_data=workflow_data)
            if event.propagation_stopped:
                break

    async def execute_handler(
        self, event: Event[Any], handler: HandlerInfo, workflow_data: dict[str, Any]
    ) -> None:
        workflow_data = {
            **workflow_data,
            'handler_info': handler,
            'router': handler.manager.router,
            'manager': handler.manager,
        }

        wrapped_handler = self._wrap_handler_with_middlewares(
            handler=handler,
            event=event,
            workflow_data=workflow_data,
        )

        try:
            await wrapped_handler()
        except Exception as e:
            event = ExceptionEvent(obj=event, exception=e)
            ...

    def _wrap_handler_with_middlewares(
        self,
        handler: HandlerInfo,
        event: Event[Any],
        workflow_data: dict[str, Any],
    ) -> WrappedWithMiddlewaresType:
        pre_execution_middlewares: list[MiddlewareCallableType] = list(
            reversed(handler.pre_execution_middlewares),
        )

        for router in handler.manager.router.chain_to_root_router:
            manager = router.get_manager_by_event(event)
            pre_execution_middlewares.extend(reversed(manager.pre_handler_middlewares))

        async def wrapper() -> Any:
            await handler.__call__(**workflow_data)

        handler_with_pre_middlewares = MiddlewareManager.wrap_callable_with_middlewares(
            middlewares=pre_execution_middlewares,
            callable_to_wrap=wrapper,
            workflow_data=workflow_data,
            first_to_last=False,
        )

        return handler_with_pre_middlewares
