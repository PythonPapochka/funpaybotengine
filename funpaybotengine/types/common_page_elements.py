from __future__ import annotations


__all__ = ('AppData', 'WebPush', 'PageHeader')


from pydantic import BaseModel
from funpayparsers.types import (
    AppData as PAppData,
    WebPush as PWebPush,
    PageHeader as PPageHeader,
)

from funpaybotengine.types.base import FunPayObject
from funpaybotengine.types.enums import Currency, Language
from funpaybotengine.types.common import MoneyValue


class WebPush(FunPayObject, BaseModel, PWebPush):
    """Represents a WebPush data extracted from an AppData dict."""

    ...


class AppData(FunPayObject, BaseModel, PAppData):
    """
    Represents an AppData dict.
    """

    locale: Language
    """Current users locale."""

    webpush: WebPush | None
    """WebPush info."""


class PageHeader(FunPayObject, BaseModel, PPageHeader):
    """
    Represents the header section of a FunPay page.

    All fields in this dataclass will be ``None`` if the response is parsed
    from a request made without authentication cookies (i.e., as an anonymous user).
    """

    language: Language
    """Current language."""

    currency: Currency
    """Current currency."""

    balance: MoneyValue | None
    """Current user balance."""
