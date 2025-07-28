from __future__ import annotations

from funpaybotengine.types.enums import OrderStatus
from funpaybotengine.storage.base import Storage


__all__ = ('InMemoryStorage',)


class InMemoryStorage(Storage):
    def __init__(self) -> None:
        self._message_ids: dict[int, int] = {}
        self._order_statuses: dict[str, OrderStatus] = {}

    async def get_last_message_id(self, chat_id: int) -> int | None:
        return self._message_ids.get(chat_id, None)

    async def set_last_message_id(self, chat_id: int, message_id: int) -> None:
        self._message_ids[chat_id] = message_id

    async def get_order_status(self, order_id: str) -> OrderStatus | None:
        return self._order_statuses.get(order_id, None)

    async def set_order_status(self, order_id: str, status: OrderStatus) -> None:
        self._order_statuses[order_id] = status
