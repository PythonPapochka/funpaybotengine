from __future__ import annotations


__all__ = ('GetSubcategoryPage',)


from typing import TYPE_CHECKING

from pydantic import BaseModel
from funpayparsers.types import Language
from funpayparsers.parsers.page_parsers import SubcategoryPageParser

from funpaybotengine.types.enums import SubcategoryType
from funpaybotengine.types.pages import SubcategoryPage
from funpaybotengine.methods.base import FunPayMethod


if TYPE_CHECKING:
    from funpayparsers.types.pages import SubcategoryPage as ParserSubcategoryPage


class GetSubcategoryPage(FunPayMethod[SubcategoryPage], BaseModel):
    """
    Get a subcategory page method (``https://funpay.com/<lots/chips>/<subcategory_id>/``).

    Returns ``funpaybotengine.types.pages.SubcategoryPage`` obj.
    """

    type: SubcategoryType
    """Subcategory type."""

    id: int
    """Subcategory ID."""

    def __init__(self, type: SubcategoryType, id: int, locale: Language | None = None):
        super().__init__(
            url=f'{type.value}s/{id}/',
            allow_anonymous=True,
            parser_cls=SubcategoryPageParser,
            locale=locale,
            type=type,
            id=id,
        )

    def transform_result(self, result: ParserSubcategoryPage) -> SubcategoryPage:
        return SubcategoryPage.model_validate(result)
