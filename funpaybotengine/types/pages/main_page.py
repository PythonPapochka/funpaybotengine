from __future__ import annotations


__all__ = ('MainPage',)

from pydantic import BaseModel

from funpaybotengine.types.chat import Chat
from funpaybotengine.types.categories import Category
from funpaybotengine.types.pages.base import FunPayPage
from funpayparsers.types.pages import MainPage as PMainPage


class MainPage(FunPayPage, BaseModel, PMainPage):
    """Represents the main page (https://funpay.com)."""

    last_categories: tuple[Category, ...]
    """Last opened categories."""

    categories: tuple[Category, ...]
    """List of categories."""

    secret_chat: Chat | None
    """
    Secret chat (ID: ``2``, name: ``'flood'``).
    
    Does not exist on EN version of the main page.
    """
