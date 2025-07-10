from __future__ import annotations


__all__ = ('BaseSession',)

from typing import TYPE_CHECKING, Any
from abc import ABC, abstractmethod
from http import HTTPStatus

from funpaybotengine.exceptions import (
    NotFound,
    Forbidden,
    BadRequest,
    Unauthorized,
    FunPayServerError,
    RateLimitExceeded,
    UnexpectedHTTPStatus,
)


if TYPE_CHECKING:
    from funpaybotengine.methods.base import FunPayMethod, MethodReturnType


_exceptions = {
    HTTPStatus.TOO_MANY_REQUESTS: RateLimitExceeded,
    HTTPStatus.UNAUTHORIZED: Unauthorized,
    HTTPStatus.FORBIDDEN: Forbidden,
    HTTPStatus.NOT_FOUND: NotFound,
    HTTPStatus.BAD_REQUEST: BadRequest,
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
            raise UnexpectedHTTPStatus(method=method, status=status_code)

        raise _exceptions[status_code](method=method)

    async def __aenter__(self) -> BaseSession:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
