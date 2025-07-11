from __future__ import annotations


__all__ = ('Message',)


from pydantic import BaseModel

from funpaybotengine.types.base import FunPayObject
from funpaybotengine.types.common import UserBadge


class Message(FunPayObject, BaseModel):
    """Represents a message from any FunPay chat (private or public)."""

    id: int
    """Unique message ID."""

    is_heading: bool
    """
    Indicates whether this is a heading message.

    Heading messages contain sender information (ID, username, etc.).
    If this is not a heading message, it means the message was sent by the same user
    as the previous one. The parser does not resolve sender data for such messages
    and sets all related fields to ``None``.
    """

    sender_id: int | None
    """Sender ID."""

    sender_username: str | None
    """Sender username."""

    badge: UserBadge | None
    """Sender's badge."""

    send_date_text: str | None
    """Message date (as human-readable text)."""

    text: str | None
    """
    Text content of the message.

    Mutually exclusive with ``Message.image_url``: 
    a message can contain either text or an image, but not both.

    Will be ``None`` if the message contains an image.
    """

    image_url: str | None
    """
    URL of the image in the message.

    Mutually exclusive with ``Message.text``: 
    a message can contain either an image or text, but not both.

    Will be ``None`` if the message contains text.
    """

    chat_id: int | str | None = None
    """Chat ID where this message was sent."""

    chat_name: str | None = None
    """Chat name (also ID) where this message was sent."""

    async def reply(self):
        raise NotImplementedError

    async def chat(self, update: bool = False):
        raise NotImplementedError

    async def chat_page(self, update: bool = False):
        raise NotImplementedError

    async def sender_profile_page(self, update: bool = False):
        raise NotImplementedError

    @property
    def type(self):
        return None
