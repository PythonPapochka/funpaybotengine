from __future__ import annotations


__all__ = ('OfferPage',)


from funpaybotengine.types.chat import Chat
from funpaybotengine.types.common import PaymentOption, DetailedUserBalance
from funpaybotengine.types.pages.base import FunPayPage


class OfferPage(FunPayPage):
    subcategory_full_name: str
    """Full name of subcategory."""

    auto_delivery: bool
    """Whether auto-delivery is on or off."""

    fields: dict[str, str]
    """Offer fields."""

    chat: Chat
    """Chat with seller."""

    payment_options: dict[str, PaymentOption]
    """Payment options in format {variant_id: PaymentOption}."""

    user_balance: DetailedUserBalance  # user_balance available even on anonymous pages
    """User balance."""
