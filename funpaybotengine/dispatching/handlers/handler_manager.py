from __future__ import annotations


__all__ = ('HandlerManager', 'HandlerCallable')

import sys
import inspect
import pathlib
from typing import TYPE_CHECKING, Any, Type, ParamSpec, TypeVar, Concatenate, Generic, overload
from types import MappingProxyType
from collections.abc import Callable, Awaitable, AsyncGenerator

from funpaybotengine.dispatching.events.base import Event
from funpaybotengine.dispatching.filters.base import Filter
from funpaybotengine.dispatching.handlers.handler import Handler


if TYPE_CHECKING:
    from funpaybotengine.dispatching.routers.base import Router


EventType = TypeVar('EventType', bound=Any)

P = ParamSpec('P')
R = TypeVar('R', bound=Any)
HandlerCallable = Callable[Concatenate[EventType, P], Awaitable[R]]
Decorator = Callable[
    [HandlerCallable[EventType, P, R]],
    HandlerCallable[EventType, P, R]
]


class HandlerManager(Generic[EventType]):
    """
    Manages the registration and filtering of event handlers for a specific event type.

    This class acts as a container and dispatcher for `Handler` instances, responsible for:

    - Registering handlers via ``register_handler`` or ``__call__``.
    - Ensuring handler ID uniqueness across the entire router network (global ID deduplication).
    - Filtering handlers based on event type and filter attached to handler.
    - Providing read-only access to all registered handlers.

    Each ``HandlerManager`` is attached to a specific ``Router`` and can optionally be bound to a
    specific ``Event`` subclass via ``event_type_filter``, which restricts dispatching
    to events of that exact type (excluding subclasses).

    Handlers can be registered via ``@manager`` / ``@manager(...)`` decorators.

    :param router: The `Router` instance this manager is associated with.
    :param event_type_filter: Optional `Event` type to restrict the handlers managed by this instance.
                              If set, only events of this exact type (`type(event) is event_type_filter`)
                              will be processed.
    """

    def __init__(self, router: Router, event_type_filter: Type[EventType] | None = None) -> None:
        self._handlers: dict[str, Handler] = {}
        self._handlers_mapping_proxy = MappingProxyType(self._handlers)
        self._router = router
        self._event_type_filter = event_type_filter

    def _register_handler(self, handler: Handler) -> None:
        """
        Registers handler to this handler manager.

        Before registration, traverses the entire router network (starting from the root router)
        to check for duplicate handler IDs. If a handler with the same ID is found anywhere
        in the network, raises a ``ValueError``.

        :param handler: ``Handler`` instance to register.

        :raises ValueError: if a handler with the same ID already exists in the router network.
        """
        root_router = self._router.root_router

        if (exists_handler := root_router.get_handler_by_id(handler.id)) is not None:
            raise ValueError(
                f'Handler with ID {handler.id} already exists.\n'
                
                f'Original handler in router \'{exists_handler.manager.router.id}\' '
                f'in \"{inspect.getsourcefile(exists_handler.callable)}:'
                f'{inspect.getsourcelines(exists_handler.callable)[1]}\"\n'
                
                f'Duplicate handler in router \'{handler.manager.router.id}\' '
                f'in \"{inspect.getsourcefile(handler.callable)}:'
                f'{inspect.getsourcelines(handler.callable)[1]}\"')
        self._handlers[handler.id] = handler

    def remove_handler(self, handler_id: str) -> Handler | None:
        """
        Removes handler from this handler manager.

        :returns: deleted ``Handler`` instance or ``None``, if ID was not found.
        """
        return self._handlers.pop(handler_id, None)

    async def filter_handlers(self, event: Event[Any]) -> AsyncGenerator[Handler, None]:
        if not self.check_event_type(event):
            return

        for handler in self._handlers.values():
            if handler.event_type_filter is not None and not isinstance(event, handler.event_type_filter):
                continue

            if handler.filter is None:
                yield handler
            else:
                filter_result = await handler.filter(event)
                if filter_result:
                    yield handler

    def check_event_type(self, event: Event[Any]) -> bool:
        """
        Checks that event type is the same as managers event type.

        :param event: event instance to check.

        :return: ``True`` if event type is same as managers event type, otherwise ``False``.
        """
        if self.event_type_filter is None or self.event_type_filter is Event:
            return True

        return type(event) is self.event_type_filter

    def register_handler(
            self,
            func: HandlerCallable[EventType, P, R] | None = None,
            *,
            event_type: Type[Event[Any]] | None = None,
            id: str | None = None,
            filter: Filter | None = None,
    ) -> None:
        if self.event_type_filter is not None and event_type is not None:
            raise ValueError(f'Cannot specify event type when using this handler manager.\n'
                             f'Use @<Router>.on_event(event_type={event_type.__name__}) instead.')

        handler_obj = Handler(
            id=id or gen_default_handler_id(func),  # type: ignore
            event_type_filter=self.event_type_filter if self.event_type_filter is not None
            else event_type,
            filter=filter,
            callable=func,  # type: ignore
            manager=self,
        )
        self._register_handler(handler_obj)

    @overload
    def __call__(
            self,
            func: HandlerCallable[EventType, P, R] = ...,
            *,
            event_type: None = ...,
            id: None = ...,
            filter: None = ...
    ) -> HandlerCallable[EventType, P, R]:
        ...

    @overload
    def __call__(
            self,
            func: None = ...,
            *,
            event_type: Type[Event[Any]] | None = ...,
            id: str | None = ...,
            filter: Filter | None = ...
    ) -> Decorator[EventType, P, R]:
        ...

    def __call__(
            self,
            func: HandlerCallable[EventType, P, R] | None = None,
            *,
            event_type: Type[Event[Any]] | None = None,
            id: str | None = None,
            filter: Filter | None = None,
    ) -> HandlerCallable[EventType, P, R] | Decorator[EventType, P, R]:
        def inner(func: HandlerCallable[EventType, P, R]) -> HandlerCallable[EventType, P, R]:
            self.register_handler(
                func=func,
                event_type=event_type,
                id=id,
                filter=filter,
            )
            return func

        if func is None:
            return inner
        return inner(func)

    @property
    def handlers(self) -> MappingProxyType[str, Handler]:
        """
        A read-only mapping of handler IDs to their corresponding ``Handler`` instances,
        registered in this manager.
        """
        return self._handlers_mapping_proxy

    @property
    def router(self) -> Router:
        """
        An instance of ``Router`` to which this manager is attached.
        :return:
        """
        return self._router

    @property
    def event_type_filter(self) -> Type[Event[Any]] | None:
        return self._event_type_filter


def gen_default_handler_id(func: HandlerCallable[Any, Any, Any]) -> str:
    func_file = pathlib.Path(inspect.getfile(func)).resolve()

    main_file = pathlib.Path(sys.modules['__main__'].__file__).resolve()
    project_root = main_file.parent

    try:
        rel_path = func_file.relative_to(project_root).with_suffix('')
    except ValueError:
        rel_path = func_file.with_suffix('')

    module_path = '.'.join(rel_path.parts)

    return f'{module_path}.{func.__qualname__}'
