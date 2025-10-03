from __future__ import annotations


__all__ = ('Storage',)

from abc import ABC, abstractmethod

from funpaybotengine.types.chat import PrivateChatPreview
from funpaybotengine.types.orders import OrderPreview


class Storage(ABC):
    @abstractmethod
    async def get_chat(self, chat_id: int) -> PrivateChatPreview | None: ...

    @abstractmethod
    async def update_chat(self, chat: PrivateChatPreview) -> None: ...

    @abstractmethod
    async def update_chats(self, *chats: PrivateChatPreview) -> None: ...

    @abstractmethod
    async def get_order(self, order_id: str) -> OrderPreview | None: ...

    @abstractmethod
    async def update_order(self, order: OrderPreview) -> None: ...

    @abstractmethod
    async def update_orders(self, *orders: OrderPreview) -> None: ...

    @abstractmethod
    async def mark_message_as_sent_by_bot(self, message_id: int, by_bot: bool = True) -> None: ...

    @abstractmethod
    async def is_message_sent_by_bot(self, message_id: int) -> bool: ...