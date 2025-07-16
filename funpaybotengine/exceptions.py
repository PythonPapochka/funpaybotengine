from __future__ import annotations


__all__ = (
    'FunPayRequestError',
    'UnexpectedHTTPStatusError',
    'RateLimitExceededError',
    'UnauthorizedError',
    'ForbiddenError',
    'BadRequestError',
    'NotFoundError',
    'FunPayServerError',
)

from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from funpaybotengine.methods.base import FunPayMethod


class FunPayRequestError(Exception):
    def __init__(self, method: FunPayMethod[Any]) -> None:
        self.method = method


class UnexpectedHTTPStatusError(FunPayRequestError):
    def __init__(self, method: FunPayMethod[Any], status: int):
        super().__init__(method=method)
        self.status = status
        self.expected_status_codes = method.expected_status_codes

    def __str__(self) -> str:
        return (
            f'Unexpected response status code {self.status} for {self.method.url!r} '
            f'(expected: {self.method.expected_status_codes!r})'
        )


class RateLimitExceededError(UnexpectedHTTPStatusError):
    def __init__(self, method: FunPayMethod[Any], status: int = 429):
        super().__init__(method=method, status=status)


class UnauthorizedError(UnexpectedHTTPStatusError):
    def __init__(self, method: FunPayMethod[Any], status: int = 401):
        super().__init__(method=method, status=status)


class ForbiddenError(UnexpectedHTTPStatusError):
    def __init__(self, method: FunPayMethod[Any], status: int = 403):
        super().__init__(method=method, status=status)


class BadRequestError(UnexpectedHTTPStatusError):
    def __init__(self, method: FunPayMethod[Any], status: int = 400):
        super().__init__(method=method, status=status)


class NotFoundError(UnexpectedHTTPStatusError):
    def __init__(self, method: FunPayMethod[Any], status: int = 404):
        super().__init__(method=method, status=status)


class FunPayServerError(UnexpectedHTTPStatusError):
    def __init__(self, method: FunPayMethod[Any], status: int = 500):
        super().__init__(method=method, status=status)
