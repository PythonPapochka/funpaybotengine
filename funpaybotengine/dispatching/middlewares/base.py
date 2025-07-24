from __future__ import annotations

__all__ = ('Middleware', 'MiddlewareManager')


from abc import ABC, abstractmethod
from funpaybotengine.dispatching.bases import MiddlewareCallableType, MiddlewareManagerDecoratorType
from typing import Any, ParamSpec, TypeVar, overload
from collections.abc import Sequence

P = ParamSpec('P')
R = TypeVar('R')
T = TypeVar('T')


class Middleware(ABC):

    @abstractmethod
    async def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


class MiddlewareManager(ABC, Sequence[MiddlewareCallableType[..., Any]]):

    @abstractmethod
    def register_middleware(self, middleware: MiddlewareCallableType[P, R]) -> MiddlewareCallableType[P, R]: ...

    @overload
    def __call__(self, middleware: None = ...) -> MiddlewareManagerDecoratorType[P, R]: ...

    @overload
    def __call__(self, middleware: MiddlewareCallableType[P, R] = ...) -> MiddlewareCallableType[P, R]: ...

    @abstractmethod
    def __call__(self, middleware: MiddlewareCallableType[P, R] | None = None) -> MiddlewareCallableType[P, R] | MiddlewareManagerDecoratorType[P, R]: ...
