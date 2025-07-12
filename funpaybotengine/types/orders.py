from __future__ import annotations


__all__ = ('OrderPreview', 'OrderPreviewsBatch')


from pydantic import BaseModel
from funpayparsers.types import (
    OrderPreview as POrderPreview,
    OrderPreviewsBatch as POrderPreviewsBatch,
)

from funpaybotengine.types.base import FunPayObject
from funpaybotengine.types.enums import OrderStatus
from funpaybotengine.types.common import MoneyValue, UserPreview


class OrderPreview(FunPayObject, BaseModel, POrderPreview):
    """Represents an order preview."""

    status: OrderStatus
    """Order status."""

    total: MoneyValue
    """Order total."""

    counterparty: UserPreview
    """Associated counterparty info."""


class OrderPreviewsBatch(FunPayObject, BaseModel, POrderPreviewsBatch):
    """
    Represents a single batch of order previews.

    This batch contains a portion of all available order previews (typically 100),
    along with metadata required to fetch the next batch.
    """

    orders: tuple[OrderPreview, ...]
    """List of order previews included in this batch."""
