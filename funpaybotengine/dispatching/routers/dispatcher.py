from __future__ import annotations


__all__ = ('Dispatcher',)


import time
import asyncio
from typing import TYPE_CHECKING, Any

from funpaybotengine.loggers import dispatcher_logger
from funpaybotengine.dispatching.bases import MiddlewareCallableType
from funpaybotengine.dispatching.events.base import ExceptionEvent
from funpaybotengine.dispatching.middlewares import (
    MiddlewareManager,
    WrappedWithMiddlewaresCallable,
)
from funpaybotengine.dispatching.routers.base import Router


if TYPE_CHECKING:
    from funpaybotengine.dispatching.bases import HandlerInfo
    from funpaybotengine.dispatching.events.base import Event


class Dispatcher(Router):
    def __init__(self, workflow_data: dict[str, Any] | None = None) -> None:
        super().__init__(name='Dispatcher')

        self._workflow_data = workflow_data or {}

    async def propagate_event(
        self,
        event: Event[Any],
        events_stack: tuple[Event[Any], ...] | None = None,
    ) -> None:
        dispatcher_logger.debug(f'New event {id(event)}: {type(event)}')

        workflow_data = {
            **self._workflow_data,
            **event.workflow_dict,
            'event': event,
            'dispatcher': self,
            'events_stack': events_stack or (event,),
            'bot': event.bot,
        }

        executed_handlers: dict[str, bool] = {}
        awaiting_handlers: list[HandlerInfo] = []

        async for handler, e in self.get_matching_handlers(event, workflow_data=workflow_data):
            if e is not None:
                error_event = ExceptionEvent(object=e, event=event)  # todo: error
                dispatcher_logger.debug(
                    f'({id(event)}) An error occurred while executing '
                    f"handler '{handler.name}' filters.",
                    exc_info=e,
                )
                continue

            if not handler.can_be_executed(executed_handlers):
                dispatcher_logger.debug(
                    f"{id(event)} Execution of handler '{handler.name}'"
                    f' delayed because of `ensure_after`.',
                )
                awaiting_handlers.append(handler)
                continue

            r = await self.execute_handler(event, handler, workflow_data=workflow_data)
            executed_handlers[handler.name] = r

            if event.propagation_stopped:
                dispatcher_logger.debug(f'({id(event)}) Event propagation stopped.')
                break

            while True:
                for awaiting_handler in awaiting_handlers:
                    if not awaiting_handler.can_be_executed(executed_handlers):
                        continue

                    awaiting_handlers.remove(awaiting_handler)
                    r = await self.execute_handler(event, awaiting_handler, workflow_data)
                    executed_handlers[awaiting_handler.name] = r
                    break
                else:
                    break

    async def execute_handler(
        self,
        event: Event[Any],
        handler: HandlerInfo,
        workflow_data: dict[str, Any],
    ) -> bool:
        workflow_data = {
            **workflow_data,
            'handler_info': handler,
        }

        wrapped_handler = self._wrap_handler_with_middlewares(
            handler=handler,
            event=event,
            workflow_data=workflow_data,
        )

        dispatcher_logger.debug(f"({id(event)}) Executing handler '{handler.name}'...")
        start = time.time()
        result = True
        try:
            if not handler.as_task:
                await wrapped_handler()
            else:
                asyncio.create_task(wrapped_handler())
        except Exception as e:
            dispatcher_logger.debug(
                f"({id(event)}) An error occurred while executing handler '{handler.name}'.",
                exc_info=e,
            )
            event = ExceptionEvent(object=e, event=event)  # todo: exception
            result = False
        finally:
            dispatcher_logger.debug(
                f"({id(event)}) Handler '{handler.name}' executed in {time.time() - start} seconds.",
            )
        return result

    def _wrap_handler_with_middlewares(
        self,
        handler: HandlerInfo,
        event: Event[Any],
        workflow_data: dict[str, Any],
    ) -> WrappedWithMiddlewaresCallable:
        pre_execution_middlewares: list[MiddlewareCallableType] = list(
            reversed(handler.middlewares),
        )

        for router in handler.manager.router.chain_to_root_router:
            manager = router.get_manager_by_event(event)
            pre_execution_middlewares.extend(reversed(manager.handler_middlewares))

        handler_with_pre_middlewares = MiddlewareManager.wrap_callable_with_middlewares(
            middlewares=pre_execution_middlewares,
            callable_to_wrap=handler.callable,
            workflow_data=workflow_data,
            first_to_last=False,
        )

        return handler_with_pre_middlewares
