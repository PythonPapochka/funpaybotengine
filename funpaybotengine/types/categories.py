__all__ = ('Category', 'Subcategory')

from funpaybotengine.types.base import FunPayObject
from funpaybotengine.types.enums import SubcategoryType
from pydantic import BaseModel


class Category(FunPayObject, BaseModel):
    """
    Represents a category from FunPay main page.
    """

    name: str
    """Category name."""

    subcategories: list['Subcategory']
    """List of subcategories."""


class Subcategory(FunPayObject, BadeModel):
    """
    Represents a subcategory from FunPay main page.
    """

    id: int
    """
    Subcategory ID.

    :warning: Subcategory ID is not unique. 
    IDs are unique per subcategory type but may repeat across types.
    """

    name: str
    """Subcategory name."""

    type: SubcategoryType
    """Subcategory type."""
