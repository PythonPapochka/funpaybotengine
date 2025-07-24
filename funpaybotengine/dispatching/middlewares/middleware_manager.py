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
    """
    Represents a callable object wrapped in a chain of middlewares.

    This class allows executing a middleware chain and
    accessing the result of the final (original) callable.
    It is typically returned by the ``MiddlewareManager.wrap_callable_with_middlewares``
    function and is meant to be awaited as ``await obj()``.

    After invocation, ``callable_executed`` will be set to ``False`` if the original callable
    was successfully executed and its result with be stored in ``callable_return``.

    :param wrapped_callable:
        The fully wrapped callable (with all middlewares applied).
        This callable should not be passed manually in normal usage; it's set by the wrapper utility.
    """

    def __init__(self, wrapped_callable: Callable[[], Awaitable[Any]] | None = None, /):
        self.wrapped_callable = wrapped_callable
        self.callable_executed: bool = False
        self.callable_return: Any = None

    async def __call__(self) -> Any:
        assert self.wrapped_callable is not None

        await self.wrapped_callable()
        return self.callable_return


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
        """
        Wraps the given callable into a middleware chain.

        Each middleware must be a callable object (either asynchronous or synchronous).
        Both the middlewares and the original callable may have arbitrary signatures —
        all required arguments will be injected from the provided ``workflow_data`` dictionary.

        In addition to ``workflow_data``, each middleware (but not the original callable)
        receives a ``next_call`` argument, which represents the next step in the middleware chain.
        To continue the chain, the middleware must explicitly call ``await next_call()``.
        If ``next_call`` is not present in the middleware's signature, it will not be passed,
        and the chain will not continue beyond that middleware.

        Internally, a ``CallableInfo`` object is created for each callable
        (middlewares and the original),  which resolves its signature and injects the
        required arguments from ``workflow_data``.

        :param middlewares:
            A sequence of middleware callables that will wrap the original callable.

        :param callable_to_wrap:
            The original callable to be executed at the end of the middleware chain.

        :param workflow_data:
            A dictionary of keyword arguments used to populate parameters for all callables in the chain.

        :param first_to_last:
            If ``True`` (default), middlewares are applied in the given order (first wraps first);
            if ``False``, middlewares are applied in reverse order.

        :returns:
            A ``WrappedWithMiddlewaresCallable`` object.
        """

        obj = WrappedWithMiddlewaresCallable(None)

        @wraps(callable_to_wrap)
        async def last_call() -> Any:
            nonlocal obj

            handler_obj = CallableInfo(callable_to_wrap)
            result = await handler_obj(**workflow_data)

            obj.callable_executed = True
            obj.callable_return = result

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
