from __future__ import annotations


__all__ = ('HandlerManager',)

import sys
import inspect
import pathlib
from typing import Any, Type
from collections.abc import Callable, Awaitable, AsyncGenerator

from funpaybotengine.dispatching.events.base import Event
from funpaybotengine.dispatching.filters.base import Filter
from funpaybotengine.dispatching.handlers.handler import Handler


class HandlerManager:
    def __init__(self, event_type: Type[Event[Any]] | None = None) -> None:
        self.handlers: dict[str, Handler] = {}
        self.event_type = event_type

    def add_handler(self, handler: Handler) -> None:
        if handler.id in self.handlers:
            raise Exception(f'Handler with ID {handler.id} already exists.')  # todo: Exception

        self.handlers[handler.id] = handler

    def remove_handler(self, handler_id: str) -> None:
        if handler_id in self.handlers:
            del self.handlers[handler_id]

    async def find_handlers(self, event: Event[Any]) -> AsyncGenerator[Handler, None]:
        if self.event_type is not None and not isinstance(event, self.event_type):
            return

        for handler in self.handlers.values():
            if handler.event_type is not None and not isinstance(event, handler.event_type):
                continue

            if handler.filter is None:
                yield handler
            else:
                filter_result = await handler.filter(event)
                if filter_result:
                    yield handler

    def __call__(
        self,
        func: Callable[[Event[Any], ...], Awaitable[Any]] | None = None,  # type: ignore[misc]
        *,
        event_type: Type[Event[Any]] | None = None,
        id: str | None = None,
        filter: Filter | None = None,
    ) -> Any:

        if self.event_type is not None and event_type is not None:
            raise Exception('Cannot assign event type to this handler.')  # todo: exception


        def inner(
                handler: Callable[[Event[Any], ...], Awaitable[Any]]  # type: ignore[misc]
        ) -> Callable[[Event[Any], ...], Awaitable[Any]]:  # type: ignore[misc]
            handler_obj = Handler(
                id=id or gen_default_handler_id(handler),
                event_type=self.event_type if event_type is not None else event_type,
                filter=filter,
                callable=handler
            )
            self.add_handler(handler_obj)
            return handler

        if func is None:
            return inner
        return inner(func)


def gen_default_handler_id(func: Callable[..., Any]) -> str:
    func_file = pathlib.Path(inspect.getfile(func)).resolve()

    main_file = pathlib.Path(sys.modules['__main__'].__file__).resolve()
    project_root = main_file.parent

    try:
        rel_path = func_file.relative_to(project_root).with_suffix('')
    except ValueError:
        rel_path = func_file.with_suffix('')

    module_path = '.'.join(rel_path.parts)

    return f'{module_path}.{func.__qualname__}'
