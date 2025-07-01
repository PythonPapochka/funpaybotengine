__all__ = ('OrderCounterpartyInfo', 'OrderPreview', 'OrderPreviewsBatch')


from funpaybotengine.types.base import FunPayObject
from funpaybotengine.types.common import MoneyValue
from funpaybotengine.types.enums import OrderStatus

from pydantic import BaseModel


class OrderCounterpartyInfo(FunPayObject, BaseModel):
    """
    Represents an order counterparty details.

    Represents the other participant of the order
    (buyer or seller, depending on the context).
    """

    id: int
    """Counterparty ID."""

    username: str
    """Counterparty username."""

    online: bool
    """True, if counterparty is online."""

    banned: bool
    """True, if counterparty is banned."""

    status_text: str
    """Status text (online / banned / last seen online)."""

    avatar_url: str
    """Counterpart avatar URL."""


class OrderPreview(FunPayObject, BaseModel):
    """
    Represents an order preview.
    """

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

    counterparty: OrderCounterpartyInfo
    """Associated counterparty info."""


class OrderPreviewsBatch(FunPayObject, BaseModel):
    """
    Represents a single batch of order previews returned by FunPay.

    This batch contains a portion of all available order previews (typically 100),
    along with metadata required to fetch the next batch.
    """

    orders: list[OrderPreview]
    """List of order previews included in this batch."""

    next_order_id: str | None
    """
    ID of the next order to use as a cursor for pagination.

    If present, this value should be included in the next request to fetch
    the following batch of order previews. If `None`, there are no more orders to load.
    """
