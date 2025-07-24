from __future__ import annotations


__all__ = ('MiddlewareManager',)


from typing import TYPE_CHECKING, Any, TypeVar, Callable, Awaitable, ParamSpec, overload
from functools import wraps
from collections.abc import Sequence

from funpaybotengine.dispatching.bases import (
    CallableInfo,
    MiddlewareCallableType,
    WrappedWithMiddlewaresType,
    MiddlewareManagerDecoratorType,
)


if TYPE_CHECKING:
    from funpaybotengine.dispatching.handlers.handler_manager import HandlerManager


P = ParamSpec('P')
R = TypeVar('R')


class MiddlewareManager(Sequence[MiddlewareCallableType[..., Any]]):
    def __init__(self, handler_manager: HandlerManager[Any]):
        self._handler_manager = handler_manager

        self._middlewares: list[MiddlewareCallableType[..., Any]] = []

    def register_middleware(
        self,
        middleware: MiddlewareCallableType[P, R],
    ) -> MiddlewareCallableType[P, R]:
        self._middlewares.append(middleware)
        return middleware

    @overload
    def __call__(self, middleware: None = ...) -> MiddlewareManagerDecoratorType[P, R]: ...

    @overload
    def __call__(
        self,
        middleware: MiddlewareCallableType[P, R] = ...,
    ) -> MiddlewareCallableType[P, R]: ...

    def __call__(
        self,
        middleware: MiddlewareCallableType[P, R] | None = None,
    ) -> MiddlewareCallableType[P, R] | MiddlewareManagerDecoratorType[P, R]:
        if middleware is None:
            return self.register_middleware
        else:
            return self.register_middleware(middleware)

    @overload
    def __getitem__(self, index: int) -> MiddlewareCallableType[..., Any]: ...

    @overload
    def __getitem__(self, index: slice) -> list[MiddlewareCallableType[..., Any]]: ...

    def __getitem__(
        self,
        index: int | slice,
    ) -> MiddlewareCallableType[Any, Any] | list[MiddlewareCallableType[..., Any]]:
        return self._middlewares[index]

    def __len__(self) -> int:
        return len(self._middlewares)

    @property
    def handler_manager(self) -> HandlerManager[Any]:
        return self._handler_manager

    @staticmethod
    def wrap_callable_with_middlewares(
        middlewares: Sequence[MiddlewareCallableType[..., Any]],
        handler_to_wrap: Callable[..., Any],
        workflow_data: dict[str, Any],
    ) -> WrappedWithMiddlewaresType:
        @wraps(handler_to_wrap)
        async def wrapper() -> Any:
            handler_obj = CallableInfo(handler_to_wrap)
            workflow_data.pop('next_call', None)
            return await handler_obj(**workflow_data)

        current: Callable[[], Awaitable[Any]] = wrapper

        for middleware in reversed(middlewares):
            current = MiddlewareManager._make_wrapper(current, middleware, workflow_data)
        return current

    @staticmethod
    def _make_wrapper(
        current: Callable[[], Any],
        middleware: MiddlewareCallableType[..., Any],
        workflow_data: dict[str, Any],
    ) -> WrappedWithMiddlewaresType:
        @wraps(middleware)
        async def middleware_wrapper() -> Any:
            next_call = CallableInfo(current)
            workflow_data['next_call'] = next_call
            middleware_obj = CallableInfo(middleware)
            return await middleware_obj(**workflow_data)

        return middleware_wrapper
