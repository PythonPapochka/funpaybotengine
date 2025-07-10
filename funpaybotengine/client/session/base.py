from __future__ import annotations


__all__ = ('BaseSession',)

from typing import TYPE_CHECKING, Any
from abc import ABC, abstractmethod
from http import HTTPStatus

from funpaybotengine.exceptions import (
    NotFoundError,
    ForbiddenError,
    BadRequestError,
    FunPayServerError,
    UnauthorizedError,
    RateLimitExceededError,
    UnexpectedHTTPStatusError,
)


if TYPE_CHECKING:
    from funpaybotengine.methods.base import FunPayMethod, MethodReturnType


_exceptions = {
    HTTPStatus.TOO_MANY_REQUESTS: RateLimitExceededError,
    HTTPStatus.UNAUTHORIZED: UnauthorizedError,
    HTTPStatus.FORBIDDEN: ForbiddenError,
    HTTPStatus.NOT_FOUND: NotFoundError,
    HTTPStatus.BAD_REQUEST: BadRequestError,
}


class BaseSession(ABC):
    @abstractmethod
    async def close(self) -> None: ...

    @abstractmethod
    async def make_request(
        self, method: FunPayMethod[MethodReturnType], timeout: float | None = None
    ) -> MethodReturnType: ...

    def check_status_code(
        self, method: FunPayMethod[Any], status_code: int | HTTPStatus
    ):
        if status_code in method.expected_status_codes:
            return

        if status_code >= HTTPStatus.INTERNAL_SERVER_ERROR:
            raise FunPayServerError(method=method)

        if status_code not in _exceptions:
            raise UnexpectedHTTPStatusError(method=method, status=status_code)

        raise _exceptions[status_code](method=method)

    async def __aenter__(self) -> BaseSession:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
