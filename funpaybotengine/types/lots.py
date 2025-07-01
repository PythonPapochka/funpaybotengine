__all__ = ('LotPreview', 'LotSeller', 'LotFields')

from funpaybotengine.types.base import FunPayObject
from funpaybotengine.types.common import MoneyValue
from pydantic import BaseModel, Field


class LotSeller(FunPayObject, BaseModel):
    """
    Represents the seller of a lot.

    Used in lot previews.
    """

    id: int
    """The seller's user ID."""

    username: str
    """The seller's username."""

    online: bool
    """Whether the seller is currently online."""

    avatar_url: str
    """URL of the seller's avatar."""

    register_date_text: str
    """The seller's registration date (as a formatted string)."""

    rating: int
    """The seller's rating (number of stars)."""

    reviews_amount: int
    """The total number of reviews received by the seller."""


class LotPreview(FunPayObject, BaseModel):
    """
    Represents a lot preview.
    """

    id: int | str
    """Unique lot ID."""

    auto_issue: bool
    """Whether auto-issue is enabled for this lot."""

    is_pinned: bool
    """Whether this lot is pinned to the top of the list."""

    desc: str | None
    """The description of the lot, if provided."""

    amount: int | None
    """The quantity of goods available in this lot, if specified."""

    price: MoneyValue
    """The price of the lot."""

    seller: LotSeller | None
    """Information about the lot seller, if applicable."""

    other_data: dict[str, str | int]
    """
    Additional data related to the lot, such as server ID, side ID, etc., 
        if applicable.
    """

    other_data_names: dict[str, str]
    """
    Human-readable names corresponding to entries in `other_data`, if applicable.
    Not all entries, that are exists in other_data can be found here.
    """


class LotFields(FunPayObject, BaseModel):
    """
    Represents lot fields.
    """

    csrf_token: str
    """User CSRF token."""

    other_fields: dict[str, str | int] = Field(default_factory=dict)
    """Other lot fields."""
