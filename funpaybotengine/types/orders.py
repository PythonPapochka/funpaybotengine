from __future__ import annotations


__all__ = ('OrderPreview', 'OrderPreviewsBatch')


from typing import Any

from pydantic import BaseModel, PrivateAttr, computed_field

from funpaybotengine.types.base import FunPayObject
from funpaybotengine.types.enums import OrderStatus, OrderPreviewType
from funpaybotengine.types.common import MoneyValue, UserPreview


class OrderPreview(FunPayObject, BaseModel):
    """Represents an order preview."""

    def model_post_init(self, context: dict[Any, Any]) -> None:
        if context and context.get('order_preview_type') is not None:
            self._type = context['order_preview_type']

    id: str
    """Order ID."""

    date_text: str
    """Order date (as human-readable text)."""

    title: str
    """Order title."""

    category_text: str
    """Order category and subcategory text."""

    status: OrderStatus
    """Order status."""

    total: MoneyValue
    """Order total."""

    counterparty: UserPreview
    """Associated counterparty info."""

    _type: OrderPreviewType = PrivateAttr(OrderPreviewType.UNKNOWN)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def type(self) -> OrderPreviewType:
        return self._type


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
