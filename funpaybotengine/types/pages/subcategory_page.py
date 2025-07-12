from __future__ import annotations


__all__ = ('SubcategoryPage',)


from pydantic import BaseModel

from funpaybotengine.types.enums import SubcategoryType
from funpaybotengine.types.offers import OfferPreview
from funpaybotengine.types.categories import Subcategory
from funpaybotengine.types.pages.base import FunPayPage
from funpayparsers.types.pages import SubcategoryPage as PSubcategoryPage


class SubcategoryPage(FunPayPage, BaseModel, PSubcategoryPage):
    """
    Represents a subcategory offers list page
    (`https://funpay.com/<lots/chips>/<subcategory_id>/`)
    """

    subcategory_type: SubcategoryType
    """Subcategory type."""

    related_subcategories: tuple[Subcategory, ...] | None
    """List of related subcategories (including this one), if exists."""

    offers: tuple[OfferPreview, ...] | None
    """Subcategory offers list."""
