from __future__ import annotations


__all__ = ('GetOrderPage',)


from pydantic import BaseModel
from funpayparsers.types import Language
from funpayparsers.parsers.page_parsers import OrderPageParser

from funpaybotengine.types.pages import OrderPage
from funpaybotengine.methods.base import FunPayMethod


class GetOrderPage(FunPayMethod[OrderPage], BaseModel):
    """
    Get an order page method (``https://funpay.com/orders/<order_id>/``).

    Returns ``funpaybotengine.types.pages.OrderPage`` obj.
    """

    id: str
    """Order ID."""

    __model_to_build__ = OrderPage

    def __init__(self, id: str, locale: Language | None = None):
        super().__init__(
            url=f'orders/{id}/',
            parser_cls=OrderPageParser,
            locale=locale,
            id=id,
        )
