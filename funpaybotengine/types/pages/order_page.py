from __future__ import annotations


__all__ = ('OrderPage',)


from typing import Annotated
from types import MappingProxyType
from collections.abc import Mapping

from pydantic import BaseModel, BeforeValidator
from funpayparsers.types.pages import OrderPage as POrderPage

from funpaybotengine.types.chat import Chat
from funpaybotengine.types.reviews import Review
from funpaybotengine.types.pages.base import FunPayPage


class OrderPage(FunPayPage, BaseModel, POrderPage):
    """Represents an order page (`https://funpay.com/orders/<order_id>/`)."""

    delivered_goods: tuple[str, ...] | None
    """List of delivered goods."""

    images: tuple[str, ...] | None
    """List of attached images."""

    data: Annotated[Mapping[str, str], BeforeValidator(OrderPage._convert_to_immutable)]
    """Order data (short description, full description, etc.)"""

    review: Review | None
    """Order review."""

    chat: Chat
    """Chat with counterparty."""

    @staticmethod
    def _convert_to_immutable(value):
        return MappingProxyType(value)
