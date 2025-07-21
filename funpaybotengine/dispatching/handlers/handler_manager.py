from __future__ import annotations


__all__ = ('HandlerManager',)

import sys
import inspect
import pathlib
from typing import TYPE_CHECKING, Any, Type
from types import MappingProxyType
from collections.abc import Callable, Awaitable, AsyncGenerator

from funpaybotengine.dispatching.events.base import Event
from funpaybotengine.dispatching.filters.base import Filter
from funpaybotengine.dispatching.handlers.handler import Handler


if TYPE_CHECKING:
    from funpaybotengine.dispatching.routers.base import Router


class HandlerManager:
    def __init__(self, router: Router, event_type: Type[Event[Any]] | None = None) -> None:
        self._handlers: dict[str, Handler] = {}
        self._handlers_mapping_proxy = MappingProxyType(self._handlers)
        self._router = router
        self._event_type = event_type

    def add_handler(self, handler: Handler) -> None:
        root_router = self._router.root_router

        if (exists_handler := root_router.get_handler_by_id(handler.id)) is not None:
            exists_function_file_path = inspect.getsourcefile(exists_handler.callable)
            exists_line_no = inspect.getsourcelines(exists_handler.callable)[1]

            function_file_path = inspect.getsourcefile(handler.callable)
            line_no = inspect.getsourcelines(handler.callable)[1]

            raise ValueError(
                f'Handler with ID {handler.id} already exists.\n'
                
                f'Original handler in router \'{exists_handler.manager.router.id}\' '
                f'in \"{exists_function_file_path}:{exists_line_no}\"\n'
                
                f'Duplicate handler in router \'{handler.manager.router.id}\' '
                f'in \"{function_file_path}:{line_no}\"')

        self._handlers[handler.id] = handler

    def remove_handler(self, handler_id: str) -> None:
        if handler_id in self._handlers:
            del self._handlers[handler_id]

    async def filter_handlers(self, event: Event[Any]) -> AsyncGenerator[Handler, None]:
        if self.event_type is not None and not isinstance(event, self.event_type):
            return

        for handler in self._handlers.values():
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
            raise ValueError(f'Cannot specify event type when using this handler manager.\n'
                             f'Use @<Router>.on_event(event_type={event_type.__name__}) instead.')

        def inner(
            handler: Callable[[Event[Any], ...], Awaitable[Any]],  # type: ignore[misc]
        ) -> Callable[[Event[Any], ...], Awaitable[Any]]:  # type: ignore[misc]
            handler_obj = Handler(
                id=id or gen_default_handler_id(handler),
                event_type=self.event_type if self.event_type is not None else event_type,
                filter=filter,
                callable=handler,
                manager=self,
            )
            self.add_handler(handler_obj)
            return handler

        if func is None:
            return inner
        return inner(func)

    @property
    def handlers(self) -> MappingProxyType[str, Handler]:
        return self._handlers_mapping_proxy

    @property
    def router(self) -> Router:
        return self._router

    @property
    def event_type(self) -> Type[Event[Any]] | None:
        return self._event_type


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
