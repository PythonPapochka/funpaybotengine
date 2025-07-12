from __future__ import annotations


__all__ = ('Category', 'Subcategory')

from pydantic import BaseModel
from funpayparsers.types import Category as PCategory, Subcategory as PSubcategory

from funpaybotengine.types.base import FunPayObject


class Category(FunPayObject, BaseModel, PCategory):
    """Represents a category from FunPay main page."""

    subcategories: tuple['Subcategory', ...]
    """List of subcategories."""


class Subcategory(FunPayObject, BaseModel, PSubcategory):
    """Represents a subcategory from FunPay main page."""

    ...
