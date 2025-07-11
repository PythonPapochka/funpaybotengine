from __future__ import annotations


__all__ = ('GetMainPage',)

from typing import TYPE_CHECKING

from pydantic import BaseModel
from funpayparsers.parsers.page_parsers import MainPageParser

from funpaybotengine.types.pages import MainPage
from funpaybotengine.methods.base import FunPayMethod


if TYPE_CHECKING:
    from funpayparsers.types.pages import MainPage as ParserMainPage


class GetMainPage(FunPayMethod[MainPage], BaseModel):
    def __init__(self, locale: str = ''):
        super().__init__(
            url='',
            locale=locale,
            parser_cls=MainPageParser,
        )

    def transform_result(self, result: ParserMainPage) -> MainPage:
        return MainPage.model_validate(result.as_dict(), context={'bot': self._bot})
