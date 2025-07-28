from __future__ import annotations


__all__ = ('BaseSession', 'Response')

from typing import TYPE_CHECKING, Any, Generic, TypeVar
from dataclasses import dataclass
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
    from funpaybotengine.client.bot import Bot


_exceptions: dict[int, Any] = {
    HTTPStatus.TOO_MANY_REQUESTS: RateLimitExceededError,
    HTTPStatus.UNAUTHORIZED: UnauthorizedError,
    HTTPStatus.FORBIDDEN: ForbiddenError,
    HTTPStatus.NOT_FOUND: NotFoundError,
    HTTPStatus.BAD_REQUEST: BadRequestError,
}


ResponseObject = TypeVar('ResponseObject', bound=Any)


@dataclass
class Response(Generic[ResponseObject]):
    url: str
    status_code: HTTPStatus | int
    raw_response: str
    response_obj: ResponseObject
    response_cookies: dict[str, str]
    method_obj: FunPayMethod[ResponseObject]


class BaseSession(ABC):
    @abstractmethod
    async def close(self) -> None: ...

    @abstractmethod
    async def make_request(
        self,
        method: FunPayMethod[MethodReturnType],
        bot: Bot | None = None,
        timeout: float | None = None,
    ) -> Response[MethodReturnType]: ...

    def check_status_code(self, method: FunPayMethod[Any], status_code: int | HTTPStatus) -> None:
        if status_code in method.expected_status_codes:
            return

        if status_code >= HTTPStatus.INTERNAL_SERVER_ERROR:
            raise FunPayServerError(method=method, status=status_code)

        if status_code not in _exceptions:
            raise UnexpectedHTTPStatusError(method=method, status=status_code)

        raise _exceptions[status_code](method=method)

    async def __aenter__(self) -> BaseSession:
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()
