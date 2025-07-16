from __future__ import annotations


__all__ = ('GetProfilePage',)


from typing import TYPE_CHECKING

from pydantic import BaseModel
from funpayparsers.types import Language
from funpayparsers.parsers.page_parsers import ProfilePageParser

from funpaybotengine.types.pages import ProfilePage
from funpaybotengine.methods.base import FunPayMethod


if TYPE_CHECKING:
    from funpayparsers.types.pages import ProfilePage as ParserProfilePage


class GetProfilePage(FunPayMethod[ProfilePage], BaseModel):
    id: int

    def __init__(self, id: int, locale: Language | None = None):
        super().__init__(
            url=f'users/{id}/',
            allow_anonymous=True,
            parser_cls=ProfilePageParser,
            locale=locale,
            id=id,
        )

    def transform_result(self, result: ParserProfilePage) -> ProfilePage:
        return ProfilePage.model_validate(result)
