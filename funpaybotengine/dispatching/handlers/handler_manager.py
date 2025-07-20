from __future__ import annotations


__all__ = ('HandlerManager',)

import sys
import inspect
import pathlib
from typing import Any
from collections.abc import Callable, Awaitable, AsyncGenerator

from funpaybotengine.dispatching.events.base import Event
from funpaybotengine.dispatching.filters.base import Filter
from funpaybotengine.dispatching.handlers.handler import Handler


class HandlerManager:
    def __init__(self) -> None:
        self.handlers: dict[str, Handler] = {}

    def add_handler(self, handler: Handler) -> None:
        if handler.id in self.handlers:
            raise Exception(f'Handler with ID {handler.id} already exists.')  # todo: Exception

        self.handlers[handler.id] = handler

    def remove_handler(self, handler_id: str) -> None:
        if handler_id in self.handlers:
            del self.handlers[handler_id]

    async def find_handlers(self, event: Event[Any]) -> AsyncGenerator[Handler, None]:
        for handler in self.handlers.values():
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
        id: str | None = None,
        filter: Filter | None = None,
    ) -> Any:

        def inner(
                handler: Callable[[Event[Any], ...], Awaitable[Any]]  # type: ignore[misc]
        ) -> Callable[[Event[Any], ...], Awaitable[Any]]:  # type: ignore[misc]

            handler_obj = Handler(
                id=id or gen_default_handler_id(handler), filter=filter, callable=handler
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
