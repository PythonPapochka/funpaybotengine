from __future__ import annotations


__all__ = ('MainPage',)
from typing import TYPE_CHECKING

from funpaybotengine.types.pages.base import FunPayPage


if TYPE_CHECKING:
    from funpaybotengine.types.chat import Chat
    from funpaybotengine.types.categories import Category


class MainPage(FunPayPage):
    """Represents the main page (https://funpay.com)."""

    last_categories: list[Category]
    """Last opened categories."""

    categories: list[Category]
    """List of categories."""

    secret_chat: Chat | None
    """
    Secret chat (ID: ``2``, name: ``'flood'``).
    
    Does not exist on EN version of the main page.
    """
