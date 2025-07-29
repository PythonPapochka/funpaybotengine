from __future__ import annotations

from funpaybotengine.types.orders import OrderPreview
from funpaybotengine.types.chat import PrivateChatPreview
from funpaybotengine.storage.base import Storage


__all__ = ('InMemoryStorage',)


class InMemoryStorage(Storage):
    def __init__(self) -> None:
        self._chats: dict[int, PrivateChatPreview] = {}
        self._orders: dict[str, OrderPreview] = {}

    async def get_chat(self, chat_id: int) -> PrivateChatPreview | None:
        return self._chats.get(chat_id, None)

    async def update_chat(self, chat: PrivateChatPreview) -> None:
        self._chats[chat.id] = chat

    async def get_order(self, order_id: str) -> OrderPreview | None:
        return self._orders.get(order_id, None)

    async def update_order(self, order: OrderPreview) -> None:
        self._orders[order.id] = order
