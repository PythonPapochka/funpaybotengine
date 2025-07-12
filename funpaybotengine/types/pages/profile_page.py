from __future__ import annotations


__all__ = ('ProfilePage',)


from pydantic import BaseModel, BeforeValidator

from funpaybotengine.types.chat import Chat
from funpaybotengine.types.enums import SubcategoryType
from funpaybotengine.types.common import UserBadge, UserRating, Achievement
from funpaybotengine.types.offers import OfferPreview
from funpaybotengine.types.reviews import ReviewsBatch
from funpaybotengine.types.pages.base import FunPayPage
from funpayparsers.types.pages import ProfilePage as PProfilePage
from types import MappingProxyType
from collections.abc import Mapping
from typing import Annotated


class ProfilePage(FunPayPage, BaseModel, PProfilePage):
    """Represents a user profile page (`https://funpay.com/users/<user_id>`)."""

    badge: UserBadge | None
    """User badge."""

    achievements: tuple[Achievement, ...]
    """User achievements."""

    rating: UserRating | None
    """User rating."""

    offers: Annotated[
        Mapping[SubcategoryType, Mapping[int, tuple[OfferPreview, ...]]] | None,
        BeforeValidator(ProfilePage._convert_to_immutable)
    ]
    """User offers."""

    chat: Chat | None
    """Chat with user."""

    reviews: ReviewsBatch | None
    """User reviews."""

    @staticmethod
    def _convert_to_immutable(value):
        if value is None:
            return None

        for type_, offers in value.items():
            value[type_] = MappingProxyType(
                {id_: tuple(offers_list) for id_, offers_list in offers.items()}
            )
        return MappingProxyType(value)
