from __future__ import annotations


__all__ = ('ChatPage',)

from typing import TYPE_CHECKING

from pydantic import BaseModel

from funpaybotengine.types.pages.base import FunPayPage


if TYPE_CHECKING:
    from funpaybotengine.types.chat import Chat, PrivateChatInfo, PrivateChatPreview


class ChatPage(FunPayPage, BaseModel):
    """Represents a chat page (`https://funpay.com/chat/?node=<chat_id>`)."""

    chat_previews: list[PrivateChatPreview] | None
    """List of private chat previews."""

    chat: Chat | None
    """Current opened chat."""

    chat_info: PrivateChatInfo | None
    """Current opened chat info."""
