from __future__ import annotations


__all__ = ('GetMainPage',)

from typing import TYPE_CHECKING

from pydantic import BaseModel
from funpayparsers.parsers.page_parsers import MainPageParser

from funpaybotengine.types.enums import Language
from funpaybotengine.types.pages import MainPage
from funpaybotengine.methods.base import FunPayMethod


if TYPE_CHECKING:
    from funpayparsers.types.pages import MainPage as ParserMainPage


class GetMainPage(FunPayMethod[MainPage], BaseModel):
    """
    Get the main page method (``https://funpay.com/``).

    Returns ``funpaybotengine.types.pages.MainPage`` obj.
    """

    change_locale: Language | None = None
    """
    Change locale to specified.
    
    Defaults to ``None``.
    """

    def __init__(self, locale: Language | None = None, change_locale: Language | None = None):
        super().__init__(
            url='',
            locale=locale,
            parser_cls=MainPageParser,
            allow_anonymous=True,
            data={'setlocale': change_locale.value} if change_locale is not None else {},
            change_locale=change_locale,
        )

    def transform_result(self, result: ParserMainPage) -> MainPage:
        return MainPage.model_validate(result, context={'bot': self._bot})
