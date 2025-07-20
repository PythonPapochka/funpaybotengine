from __future__ import annotations


__all__ = (
    'Filter',
    'AndFilter',
    'OrFilter',
    'NotFilter',
    'FilterFromFunction',
    'FilterFromAsyncFunction',
    'any_of',
    'all_of',
)

import inspect
from typing import TYPE_CHECKING, Any, Iterable, Protocol, Awaitable
from abc import ABC, abstractmethod


if TYPE_CHECKING:
    from funpaybotengine.dispatching.events.base import Event


class CallableFilterProtocol(Protocol):
    def __call__(self, event: Event[Any], *args: Any, **kwargs: Any) -> bool: ...


class AwaitableFilterProtocol(Protocol):
    def __call__(self, event: Event[Any], *args: Any, **kwargs: Any) -> Awaitable[bool]: ...


class Filter(ABC):
    @abstractmethod
    async def __call__(self, event: Event[Any], *args: Any, **kwargs: Any) -> bool: ...

    def __and__(
        self, other: Filter | CallableFilterProtocol | AwaitableFilterProtocol
    ) -> AndFilter:
        if not isinstance(other, Filter):
            other = _convert_filters([other])[0]
        return AndFilter(self, other)

    def __or__(self, other: Filter | CallableFilterProtocol | AwaitableFilterProtocol) -> OrFilter:
        if not isinstance(other, Filter):
            other = _convert_filters([other])[0]
        return OrFilter(self, other)

    def __invert__(self) -> NotFilter:
        return NotFilter(self)


class AndFilter(Filter):
    def __init__(self, *filters: Filter) -> None:
        self._filters = filters

    async def __call__(self, event: Event[Any], *args: Any, **kwargs: Any) -> bool:
        return all(i(event, *args, **kwargs) for i in self._filters)


class OrFilter(Filter):
    def __init__(self, *filters: Filter) -> None:
        self._filters = filters

    async def __call__(self, event: Event[Any], *args: Any, **kwargs: Any) -> bool:
        return any(i(event, *args, **kwargs) for i in self._filters)


class NotFilter(Filter):
    def __init__(self, filter: Filter) -> None:
        self._filter = filter

    async def __call__(self, event: Event[Any], *args: Any, **kwargs: Any) -> bool:
        return not self._filter(event, *args, **kwargs)


class FilterFromFunction(Filter):
    def __init__(self, function: CallableFilterProtocol) -> None:
        self._function = function

    async def __call__(self, event: Event[Any], *args: Any, **kwargs: Any) -> bool:
        return self._function(event, *args, **kwargs)


class FilterFromAsyncFunction(Filter):
    def __init__(self, function: AwaitableFilterProtocol) -> None:
        self._function = function

    async def __call__(self, event: Event[Any], *args: Any, **kwargs: Any) -> bool:
        return await self._function(event, *args, **kwargs)


def _convert_filters(
    filters: Iterable[CallableFilterProtocol | AwaitableFilterProtocol | Filter],
) -> list[Filter]:
    converted_filters: list[Filter] = []
    for i in filters:
        if isinstance(i, Filter):
            converted_filters.append(i)
        elif inspect.iscoroutinefunction(i):
            converted_filters.append(FilterFromAsyncFunction(i))
        else:
            converted_filters.append(FilterFromFunction(i))  # type: ignore[arg-type]
            # checked above

    return converted_filters


def any_of(*filters: CallableFilterProtocol | AwaitableFilterProtocol | Filter) -> OrFilter:
    return OrFilter(*_convert_filters(filters))


def all_of(*filters: CallableFilterProtocol | AwaitableFilterProtocol | Filter) -> AndFilter:
    return AndFilter(*_convert_filters(filters))
