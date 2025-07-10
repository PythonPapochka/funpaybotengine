from __future__ import annotations


__all__ = (
    'FunPayRequestException',
    'UnexpectedHTTPStatus',
    'RateLimitExceeded',
    'Unauthorized',
    'Forbidden',
    'BadRequest',
    'NotFound',
    'FunPayServerError',
)

from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from funpaybotengine.methods.base import FunPayMethod


class FunPayRequestException(Exception):
    def __init__(self, method: FunPayMethod[Any]) -> None:
        self.method = method


class UnexpectedHTTPStatus(FunPayRequestException):
    def __init__(self, method: FunPayMethod[Any], status: int):
        super().__init__(method=method)
        self.status = status
        self.expected_status_codes = method.expected_status_codes

    def __str__(self):
        return (
            f'Unexpected response status code {self.status} for {self.method.url!r} '
            f'(expected: {self.method.expected_status_codes!r})'
        )


class RateLimitExceeded(UnexpectedHTTPStatus):
    def __init__(self, method: FunPayMethod[Any], status: int = 429):
        super().__init__(method=method, status=status)


class Unauthorized(UnexpectedHTTPStatus):
    def __init__(self, method: FunPayMethod[Any], status: int = 401):
        super().__init__(method=method, status=status)


class Forbidden(UnexpectedHTTPStatus):
    def __init__(self, method: FunPayMethod[Any], status: int = 403):
        super().__init__(method=method, status=status)


class BadRequest(UnexpectedHTTPStatus):
    def __init__(self, method: FunPayMethod[Any], status: int = 400):
        super().__init__(method=method, status=status)


class NotFound(UnexpectedHTTPStatus):
    def __init__(self, method: FunPayMethod[Any], status: int = 404):
        super().__init__(method=method, status=status)


class FunPayServerError(UnexpectedHTTPStatus):
    def __init__(self, method: FunPayMethod[Any], status: int = 500):
        super().__init__(method=method, status=status)
