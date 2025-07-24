from __future__ import annotations


__all__ = ('MiddlewareManager',)


from typing import Any, TypeVar, Callable, Awaitable, ParamSpec, overload
from functools import wraps
from collections.abc import Sequence

from funpaybotengine.dispatching.bases import (
    CallableInfo,
    MiddlewareCallableType,
    WrappedWithMiddlewaresType,
    MiddlewareManagerDecoratorType,
)


P = ParamSpec('P')
R = TypeVar('R')


class WrappedWithMiddlewaresCallable:
    def __init__(self, wrapped_callable: Callable[[], Awaitable[Any]] | None = None, /):
        self.wrapped_callable = wrapped_callable
        self.handler_executed: bool = False
        self.handler_execution_result: Any = None

    async def __call__(self) -> Any:
        assert self.wrapped_callable is not None

        await self.wrapped_callable()
        return self.handler_execution_result


class MiddlewareManager(Sequence[MiddlewareCallableType[..., Any]]):
    def __init__(self) -> None:
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

    @staticmethod
    def wrap_callable_with_middlewares(
        middlewares: Sequence[MiddlewareCallableType[..., Any]],
        callable_to_wrap: Callable[..., Any],
        workflow_data: dict[str, Any],
        first_to_last: bool = True,
    ) -> WrappedWithMiddlewaresCallable:

        obj = WrappedWithMiddlewaresCallable(None)

        @wraps(callable_to_wrap)
        async def last_call() -> Any:
            nonlocal obj

            handler_obj = CallableInfo(callable_to_wrap)
            result = await handler_obj(**workflow_data)

            obj.handler_executed = True
            obj.handler_execution_result = result

        current: Callable[[], Awaitable[Any]] = last_call

        for middleware in reversed(middlewares) if first_to_last else middlewares:
            current = MiddlewareManager._make_wrapper(current, middleware, workflow_data)

        obj.wrapped_callable = current
        return obj

    @staticmethod
    def _make_wrapper(
        current: Callable[[], Any],
        middleware: MiddlewareCallableType[..., Any],
        workflow_data: dict[str, Any],
    ) -> WrappedWithMiddlewaresType:
        @wraps(middleware)
        async def middleware_wrapper() -> Any:
            next_call = CallableInfo(current)
            middleware_obj = CallableInfo(middleware)
            return await middleware_obj(**workflow_data, **{'next_call': next_call})

        return middleware_wrapper
