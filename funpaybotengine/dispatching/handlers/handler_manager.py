from __future__ import annotations


__all__ = ('HandlerManager',)

import sys
import inspect
import pathlib
from typing import TYPE_CHECKING, Any, Type, Generic, TypeVar, overload
from types import MappingProxyType
from collections.abc import Callable, AsyncGenerator

from funpaybotengine.loggers import router_logger
from funpaybotengine.dispatching.bases import CallableInfo, HandlerInfo, HandlerCallableType
from funpaybotengine.dispatching.events.base import Event
from funpaybotengine.dispatching.filters.base import Filter, CallableFilter, AwaitableFilter
from funpaybotengine.dispatching.middlewares.middleware_manager import MiddlewareManager


if TYPE_CHECKING:
    from funpaybotengine.dispatching.routers.base import Router


EventType = TypeVar('EventType', bound=Any)
F = TypeVar('F', bound=HandlerCallableType)


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
    :param event_type_filter:
        Optional ``Event`` type to restrict the handlers managed by this instance.
        If set, only events of this exact type (``type(event) is event_type_filter``)
        will be processed.
    """

    def __init__(
        self,
        router: Router,
        name: str,
        event_type_filter: Type[EventType] | None = None,
    ) -> None:
        self._handlers: dict[str, HandlerInfo] = {}
        self._handlers_mapping_proxy = MappingProxyType(self._handlers)
        self._router = router
        self._event_type_filter = event_type_filter
        self._name = name

        self._pre_filters_middlewares = MiddlewareManager()
        self._pre_handler_middlewares = MiddlewareManager()

    def _register_handler(self, handler: HandlerInfo) -> None:
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
                f"Original handler in router '{exists_handler.manager.router.name}' "
                f'in "{inspect.getsourcefile(exists_handler.callable)}:'
                f'{inspect.getsourcelines(exists_handler.callable)[1]}"\n'
                f"Duplicate handler in router '{handler.manager.router.name}' "
                f'in "{inspect.getsourcefile(handler.callable)}:'
                f'{inspect.getsourcelines(handler.callable)[1]}"',
            )
        self._handlers[handler.id] = handler
        router_logger.debug(
            f'{self.router.name}.{self.name} Registered handler with ID {handler.id}.',
        )

    def remove_handler(self, handler_id: str) -> HandlerInfo | None:
        """
        Removes handler from this handler manager.

        :returns: deleted ``Handler`` instance or ``None``, if ID was not found.
        """
        return self._handlers.pop(handler_id, None)

    async def get_matching_handlers(
        self,
        event: Event[Any],
        workflow_data: dict[str, Any],
    ) -> AsyncGenerator[HandlerInfo, None]:
        """
        Executes the chain of pre-filter middlewares and yields handlers
        whose filters match the given event.

        :param event: The event object to be checked against handler filters.
        :param workflow_data: A dictionary containing data related to the current workflow.

        :return: An async generator of ``HandlerInfo`` objects with matching filters.
        """

        async def wrapped():
            return self._inner_get_matching_handlers(event, workflow_data)

        wrapped_get_matching_handlers = MiddlewareManager.wrap_callable_with_middlewares(
            middlewares=self._pre_filters_middlewares,
            callable_to_wrap=wrapped,
            workflow_data=workflow_data,
        )

        middlewares_result = await wrapped_get_matching_handlers()
        if middlewares_result.callable_executed:
            async for handler in middlewares_result.callable_return:
                yield handler

    async def _inner_get_matching_handlers(
        self,
        event: Event[Any],
        workflow_data: dict[str, Any]
    ) -> AsyncGenerator[HandlerInfo, None]:
        """
        Iterates through all registered handlers and yields those whose filters
        match the given event.

        :param event: The incoming event to check against handler filters.

        :return: An async generator yielding handlers that should handle the event.
        """

        for handler in self._handlers.values():
            if handler.event_type_filter is not None and not isinstance(
                event,
                handler.event_type_filter,
            ):
                router_logger.debug(
                    f'{self.router.name}.{self.name} skipping handler {handler.id}: '
                    f'event type {type(event)} is not {handler.event_type_filter} '
                    f'(from handler event type filter).',
                )
                continue

            if handler.filter is None:
                router_logger.debug(
                    f'{self.router.name}.{self.name} yielding handler {handler.id}: '
                    f'handler has no filter.',
                )
                yield handler
            else:
                filter_result = await handler.filter(**workflow_data)
                if filter_result:
                    router_logger.debug(
                        f'{self.router.name}.{self.name} yielding handler {handler.id}: '
                        f'handler filter result is {filter_result}.',
                    )
                    yield handler
                else:
                    router_logger.debug(
                        f'{self.router.name}.{self.name} skipping handler {handler.id}: '
                        f'handler filter result is {filter_result}.',
                    )

    def register_handler(
        self,
        func: HandlerCallableType,
        *,
        event_type: Type[Event[Any]] | None = None,
        id: str | None = None,
        filter: Filter | CallableFilter | AwaitableFilter | None = None,
        pre_execution_middlewares: list[Any] | None = None,
    ) -> None:
        if self.event_type_filter is not None and event_type is not None:
            raise ValueError(
                f'Cannot specify event type when using this handler manager.\n'
                f'Use @<Router>.on_event(event_type={event_type.__name__}) instead.',
            )

        handler_obj = HandlerInfo(
            id=id or gen_default_handler_id(func),
            event_type_filter=self.event_type_filter
            if self.event_type_filter is not None
            else event_type,
            filter=CallableInfo(filter) if filter is not None else None,
            callable=func,
            manager=self,
            pre_execution_middlewares=pre_execution_middlewares or [],
        )
        self._register_handler(handler_obj)

    @overload
    def __call__(self, func: F, /) -> F: ...

    @overload
    def __call__(
        self,
        *,
        event_type: Type[Event[Any]] | None = None,
        id: str | None = None,
        filter: Filter | CallableFilter | AwaitableFilter | None = None,
        pre_execution_middlewares: list[Any] | None = None,  # todo: middleware type
    ) -> Callable[[F], F]: ...

    def __call__(
        self,
        func: F | None = None,
        *,
        event_type: Type[Event[Any]] | None = None,
        id: str | None = None,
        filter: Filter | CallableFilter | AwaitableFilter | None = None,
        pre_execution_middlewares: list[Any] | None = None,  # todo: middleware type
    ) -> F | Callable[[F], F]:
        def inner(func: F) -> F:
            self.register_handler(
                func=func,
                event_type=event_type,
                id=id,
                filter=filter,
                pre_execution_middlewares=pre_execution_middlewares,
            )
            return func

        if func is None:
            return inner
        return inner(func)

    @property
    def handlers(self) -> MappingProxyType[str, HandlerInfo]:
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

    @property
    def name(self) -> str:
        return self._name

    @property
    def pre_filter_middlewares(self) -> MiddlewareManager:
        return self._pre_filters_middlewares

    @property
    def pre_handler_middlewares(self) -> MiddlewareManager:
        return self._pre_handler_middlewares


def gen_default_handler_id(func: HandlerCallableType) -> str:
    func_file = pathlib.Path(inspect.getfile(func)).resolve()

    main_file = pathlib.Path(sys.modules['__main__'].__file__).resolve()
    project_root = main_file.parent

    try:
        rel_path = func_file.relative_to(project_root).with_suffix('')
    except ValueError:
        rel_path = func_file.with_suffix('')

    module_path = '.'.join(rel_path.parts)

    return f'{module_path}.{func.__qualname__}'
