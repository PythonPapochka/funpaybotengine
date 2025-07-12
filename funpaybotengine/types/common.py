from __future__ import annotations


__all__ = (
    'MoneyValue',
    'UserBadge',
    'UserPreview',
    'UserRating',
    'Achievement',
    'CurrentlyViewingOfferInfo',
)


from pydantic import BaseModel
from funpayparsers.types import (
    UserBadge as PUserBadge,
    MoneyValue as PMoneyValue,
    UserRating as PUserRating,
    Achievement as PAchievement,
    UserPreview as PUserPreview,
    CurrentlyViewingOfferInfo as PCurrentlyViewingOfferInfo,
)

from funpaybotengine.types.base import FunPayObject


class MoneyValue(FunPayObject, BaseModel, PMoneyValue):
    """
    Represents a monetary value with an associated currency.

    This class is used to store money-related information, such as:
        - the price of an offer,
        - the total of an order,
        - the user balance,
        - etc.
    """

    ...


class UserBadge(FunPayObject, BaseModel, PUserBadge):
    """
    Represents a user badge.

    This badge is shown in heading messages sent by support, arbitration,
    or the FunPay issue bot, and also appears on the profile pages of support users.
    """

    ...


class UserPreview(FunPayObject, BaseModel, PUserPreview):
    """
    Represents user preview.
    """

    ...


class UserRating(FunPayObject, BaseModel, PUserRating):
    """
    Represents full user rating.
    """

    ...


class Achievement(FunPayObject, BaseModel, PAchievement):
    """Represents a user achievement."""

    ...


class CurrentlyViewingOfferInfo(
    FunPayObject, BaseModel, PCurrentlyViewingOfferInfo
): ...
