from __future__ import annotations


__all__ = ('Dispatcher',)


from typing import Any

from eventry.asyncio.dispatcher import Dispatcher as BaseDispatcher, ErrorContext

from funpaybotengine.dispatching.events import ExceptionEvent
from funpaybotengine.dispatching.routers import Router


def error_event_factory(context: ErrorContext) -> ExceptionEvent:
    return ExceptionEvent(object=context.exception, event=context.event)


class Dispatcher(BaseDispatcher, Router):
    def __init__(self, workflow_data: dict[str, Any] | None = None):
        BaseDispatcher.__init__(
            self,
            error_event_factory=error_event_factory,
            workflow_data=workflow_data,
        )

        Router.__init__(self, name='Dispatcher')
