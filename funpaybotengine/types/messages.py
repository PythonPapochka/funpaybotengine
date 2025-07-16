from __future__ import annotations


__all__ = ('Message',)


from pydantic import BaseModel, ValidationInfo, field_validator
from funpayparsers.types import Message as PMessage

from funpaybotengine.types.base import FunPayObject
from funpaybotengine.types.common import UserBadge
from funpaybotengine.base import check_bound


class Message(FunPayObject, BaseModel, PMessage):
    """Represents a message from any FunPay chat (private or public)."""

    badge: UserBadge | None
    """Sender's badge."""

    chat_id: int | str | None = None
    """Chat ID where this message was sent."""

    chat_name: str | None = None
    """Chat name (also ID) where this message was sent."""

    @field_validator('chat_id', mode='before')
    @classmethod
    def get_chat_id_from_context(cls, value, info: ValidationInfo):
        return info.context.get('chat_id') if value is None else value

    @field_validator('chat_name', mode='before')
    @classmethod
    def get_chat_name_from_context(cls, value, info: ValidationInfo):
        return info.context.get('chat_name') if value is None else value

    async def reply(self):
        raise NotImplementedError

    async def chat(self, update: bool = False):
        raise NotImplementedError

    async def chat_page(self, update: bool = False):
        raise NotImplementedError

    async def sender_profile_page(self, update: bool = False):
        raise NotImplementedError
