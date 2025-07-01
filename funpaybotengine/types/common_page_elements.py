__all__ = ('AppData', 'WebPush')


from typing import Literal
from funpaybotengine.types.base import FunPayObject
from pydantic import BaseModel


class WebPush(FunPayObject, BaseModel):
    """
    Represents a WebPush data extracted from an AppData dict.
    """

    app: str
    """App ID."""

    enabled: bool
    """Is WebPush enabled?"""

    hwid_required: bool
    """Does it requires HWID?"""


class AppData(FunPayObject, BaseModel):
    """
    Represents an AppData dict.
    """

    locale: Literal['en', 'ru', 'uk']
    """Current users locale."""

    csrf_token: str
    """CSRF token."""

    user_id: int
    """Users ID."""

    webpush: WebPush
    """WebPush info."""
