from __future__ import annotations


__all__ = ('Message',)


from typing import Any

from pydantic import BaseModel, ValidationInfo, field_validator

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

    chat_id: int | str | None
    """
    Chat ID where the message was sent.

    Parsers obtain this value from the `context` field of the provided options only.

    Context key: ``chat_id``.
    """

    chat_name: str | None
    """
    Chat name where the message was sent.

    This value is available only via the options context during parsing.

    Context key: ``chat_name``.
    """

    @field_validator('chat_id', mode='before')
    @classmethod
    def get_chat_id_from_context(cls, value: Any, info: ValidationInfo) -> Any:
        if info.context:
            return info.context.get('chat_id') if value is None else value
        return None

    @field_validator('chat_name', mode='before')
    @classmethod
    def get_chat_name_from_context(cls, value: Any, info: ValidationInfo) -> Any:
        if info.context:
            return info.context.get('chat_name') if value is None else value
        return None

    async def reply(self) -> None:
        raise NotImplementedError

    async def chat(self, update: bool = False) -> None:
        raise NotImplementedError

    async def chat_page(self, update: bool = False) -> None:
        raise NotImplementedError

    async def sender_profile_page(self, update: bool = False) -> None:
        raise NotImplementedError
