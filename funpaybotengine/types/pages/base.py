from __future__ import annotations


__all__ = ('FunPayPage',)

from typing import TYPE_CHECKING

from funpaybotengine.types.base import FunPayObject


if TYPE_CHECKING:
    from funpaybotengine.types.common_page_elements import AppData, PageHeader


class FunPayPage(FunPayObject):
    """Base class for FunPay pages."""

    header: PageHeader
    """Page header."""

    app_data: AppData
    """App data."""
