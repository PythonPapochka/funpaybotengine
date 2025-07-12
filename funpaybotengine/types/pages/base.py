from __future__ import annotations


__all__ = ('FunPayPage',)


from pydantic import BaseModel
from funpayparsers.types.pages import FunPayPage as PFunPayPage

from funpaybotengine.types.base import FunPayObject
from funpaybotengine.types.common_page_elements import AppData, PageHeader


class FunPayPage(FunPayObject, BaseModel, PFunPayPage):
    """Base class for FunPay pages."""

    header: PageHeader
    """Page header."""

    app_data: AppData
    """App data."""
