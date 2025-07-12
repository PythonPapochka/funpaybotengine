from __future__ import annotations


__all__ = ('OrderPreview', 'OrderPreviewsBatch')


from pydantic import BaseModel

from funpaybotengine.types.base import FunPayObject
from funpaybotengine.types.enums import OrderStatus
from funpaybotengine.types.common import MoneyValue, UserPreview


class OrderPreview(FunPayObject, BaseModel):
    """Represents an order preview."""

    id: str
    """Order ID."""

    date_text: str
    """Order date (as human-readable text)."""

    desc: str
    """Order description."""

    category_text: str
    """Order category and subcategory text."""

    status: OrderStatus
    """Order status."""

    total: MoneyValue
    """Order total."""

    counterparty: UserPreview
    """Associated counterparty info."""


class OrderPreviewsBatch(FunPayObject, BaseModel):
    """
    Represents a single batch of order previews.

    This batch contains a portion of all available order previews (typically 100),
    along with metadata required to fetch the next batch.
    """

    orders: tuple[OrderPreview, ...]
    """List of order previews included in this batch."""

    next_order_id: str | None
    """
    ID of the next order to use as a cursor for pagination.

    If present, this value should be included in the next request to fetch the 
    following batch of order previews. 
    
    If ``None``, there are no more orders to load.
    """
