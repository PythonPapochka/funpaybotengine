from __future__ import annotations


__all__ = ('PrivateChatPreview', 'Chat', 'PrivateChatInfo')


from pydantic import BaseModel
from funpayparsers.types import (
    Chat as PChat,
    PrivateChatInfo as PPrivateChatInfo,
    PrivateChatPreview as PPrivateChatPreview,
)

from funpaybotengine.types.base import FunPayObject
from funpaybotengine.types.common import UserPreview, CurrentlyViewingOfferInfo
from funpaybotengine.types.messages import Message


class PrivateChatPreview(FunPayObject, BaseModel, PPrivateChatPreview):
    """Represents a private chat preview."""

    ...


class Chat(FunPayObject, BaseModel, PChat):
    """Represents a chat."""

    interlocutor: UserPreview | None
    """Interlocutor preview. Available in private chats only."""

    history: tuple[Message, ...]
    """
    Messages history.
    
    - Private chats: last 50 messages.
    - Public chats: last 25 messages.
    """


class PrivateChatInfo(FunPayObject, BaseModel, PPrivateChatInfo):
    """
    Represents a private chat info.

    Located near private chat.
    """

    currently_viewing_offer: CurrentlyViewingOfferInfo | None
    """
    Info about the offer currently being viewed by the interlocutor.
    """
