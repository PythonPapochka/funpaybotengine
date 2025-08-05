from __future__ import annotations


__all__ = ('GetProfilePage',)


from pydantic import BaseModel
from funpayparsers.types import Language
from funpayparsers.parsers.page_parsers import ProfilePageParser

from funpaybotengine.types.pages import ProfilePage
from funpaybotengine.methods.base import FunPayMethod


class GetProfilePage(FunPayMethod[ProfilePage], BaseModel):
    """
    Get a profile page method (``https://funpay.com/users/<user_id>/``).

    Returns ``funpaybotengine.types.pages.ProfilePage`` obj.
    """

    id: int
    """User ID."""

    __model_to_build__ = ProfilePage

    def __init__(self, id: int, locale: Language | None = None):
        super().__init__(
            url=f'users/{id}/',
            allow_anonymous=True,
            parser_cls=ProfilePageParser,
            locale=locale,
            id=id,
        )
