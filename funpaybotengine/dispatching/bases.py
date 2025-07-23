from __future__ import annotations


__all__ = ('CallableInfo', )

from dataclasses import dataclass, field
from typing import Callable, Any, TYPE_CHECKING, Type
import asyncio
import inspect


if TYPE_CHECKING:
    from funpaybotengine.dispatching.events.base import Event
    from funpaybotengine.dispatching.filters.base import Filter
    from funpaybotengine.dispatching.handlers.handler_manager import HandlerManager


@dataclass
class CallableInfo:
    """
    Represents information about a callable.
    """

    callable: Callable[..., Any]
    """
    The callable object this info refers to.
    """

    is_awaitable: bool = field(init=False)
    """
    Indicates whether the callable is awaitable.
    """

    has_double_star_kwargs: bool = field(init=False)
    """
    Indicates whether the callable accepts ``**kwargs`` (or any other ``**`` variables).
    """

    param_names: set[str] = field(init=False)
    """
    Set of params and keyword params that accepted by ``CallableInfo.callable``.
    """

    def __post_init__(self) -> None:
        func = self.callable
        specs = inspect.getfullargspec(func)

        self.is_awaitable = inspect.isawaitable(func) or inspect.iscoroutinefunction(func)
        self.has_double_star_kwargs = specs.varkw is not None
        self.param_names = set(*specs.args, *specs.kwonlyargs)

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if not self.has_double_star_kwargs:
            kwargs = {k: v for k, v in kwargs.items() if k in self.param_names}

        if self.is_awaitable:
            return await self.callable(*args, **kwargs)
        return asyncio.to_thread(self.callable, *args, **kwargs)


@dataclass
class HandlerInfo(CallableInfo):
    id: str
    """Handler ID."""

    event_type_filter: Type[Event[Any]] | None
    """Event type on which this handler should be executed."""

    filter: Filter | None
    """Handler filter."""

    callable: Callable[..., Any]
    """Original callable."""

    manager: HandlerManager[Any]
    """Handler manager to which this handler is bound."""
