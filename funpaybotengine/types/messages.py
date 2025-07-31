from __future__ import annotations


__all__ = ('Message',)


import re
from typing import TYPE_CHECKING, Any
from io import BytesIO

from pydantic import BaseModel, PrivateAttr, ValidationInfo, field_validator

from funpaybotengine.types.base import FunPayObject
from funpaybotengine.types.enums import MessageType
from funpaybotengine.types.common import UserBadge
from funpayparsers.message_type_re import ORDER_ID


if TYPE_CHECKING:
    from funpaybotengine.types.pages.chat_page import ChatPage
    from funpaybotengine.types.pages.profile_page import ProfilePage


class _UNSET:
    pass


_unset = _UNSET()

_ORDER_RELATED_TYPES: tuple[MessageType, ...] = (
    MessageType.NEW_ORDER,
    MessageType.ORDER_CLOSED,
    MessageType.ORDER_CLOSED_BY_ADMIN,
    MessageType.ORDER_REOPENED,
    MessageType.ORDER_REFUNDED,
    MessageType.ORDER_PARTIALLY_REFUNDED,
    MessageType.NEW_FEEDBACK,
    MessageType.FEEDBACK_CHANGED,
    MessageType.FEEDBACK_DELETED,
    MessageType.NEW_FEEDBACK_REPLY,
    MessageType.FEEDBACK_REPLY_CHANGED,
    MessageType.FEEDBACK_REPLY_DELETED,
)


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

    _type: MessageType | _UNSET = PrivateAttr(default=_unset)
    _related_order_id: str | None | _UNSET = PrivateAttr(default=_unset)
    _chat_page: ChatPage | None = PrivateAttr(default=None)
    _sender_profile: ProfilePage | None = PrivateAttr(default=None)

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

    @property
    def type(self) -> MessageType:
        if not isinstance(self._type, _UNSET):
            return self._type

        if not self.sender_id == 0:
            self._type = MessageType.NON_SYSTEM
            return MessageType.NON_SYSTEM

        if not self.text:
            self._type = MessageType.UNKNOWN_SYSTEM
            return MessageType.UNKNOWN_SYSTEM

        self._type = MessageType.get_by_message_text(self.text)
        return self._type

    @property
    def related_order_id(self) -> str | None:
        if not isinstance(self._related_order_id, _UNSET):
            return self._related_order_id

        if not self.text:
            self._related_order_id = None
            return None

        if self.type not in _ORDER_RELATED_TYPES:
            self._related_order_id = None
            return None

        match = ORDER_ID.search(self.text)

        if not match:
            self._related_order_id = None
            return None

        self._related_order_id = match.group()[1:]
        return self._related_order_id

    async def reply(
        self,
        text: str | None = None,
        image: str | BytesIO | int | None = None,
        enforce_whitespaces: bool = True,
    ) -> Message:
        assert self.bot is not None
        assert self.chat_id is not None or self.chat_name is not None

        return await self.bot.send_message(
            chat_id=self.chat_id or self.chat_name,  # type: ignore[arg-type]  # todo
            text=text,  # type: ignore[arg-type]  # todo
            image=image,  # type: ignore[arg-type]  # todo
            enforce_whitespaces=enforce_whitespaces,
        )

    @property
    def from_me(self) -> bool:
        if not self.bot:
            return False
        return self.bot.userid == self.sender_id

    async def chat(self, update: bool = False) -> None:
        raise NotImplementedError

    async def chat_page(self, update: bool = False) -> ChatPage:
        assert self.bot is not None
        assert self.chat_id is not None or self.chat_name is not None

        if self._chat_page is not None and not update:
            return self._chat_page

        return await self.bot.get_chat_page(
            chat_id=self.chat_id or self.chat_name,  # type: ignore[arg-type]  # todo
        )

    async def sender_profile_page(self, update: bool = False) -> ProfilePage:
        assert self.bot is not None
        assert self.sender_id is not None

        if self._sender_profile is not None and not update:
            return self._sender_profile

        return await self.bot.get_profile_page(id=self.sender_id)
