from __future__ import annotations


__all__ = ('Refund',)


from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from funpaybotengine.types.enums import Language
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session.http_methods import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.client.session.base import Response


class Refund(FunPayMethod[bool], BaseModel):
    """
    Refund an order (``https://funpay.com/orders/refund``).

    Returns ``True``.
    """

    order_id: str
    """Order ID to refund."""

    csrf_token: str
    """CSRF token."""

    def __init__(self, order_id: str, csrf_token: str, locale: Language | None = None):
        super().__init__(
            method=HTTPMethod.POST,
            url='orders/refund',
            locale=locale,
            data={'id': order_id, 'csrf_token': csrf_token},
            headers={'X-Requested-With': 'XMLHttpRequest'},
            order_id=order_id,
            csrf_token=csrf_token,
        )

    def parse_result(self, response: Response[Any]) -> bool:
        return True

    def transform_result(self, parsing_result: Any, response: Response[Any]) -> bool:
        return True
