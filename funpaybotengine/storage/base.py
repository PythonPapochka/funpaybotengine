__all__ = ('Storage',)

from abc import ABC, abstractmethod
from funpaybotengine.types.enums import OrderStatus


class Storage(ABC):
    @abstractmethod
    async def get_last_message_id(self, chat_id: int) -> int | None: ...

    @abstractmethod
    async def set_last_message_id(self, chat_id: int, message_id: int) -> None: ...

    @abstractmethod
    async def get_order_status(self, order_id: str) -> OrderStatus | None: ...

    @abstractmethod
    async def set_order_status(self, order_id: str, status: OrderStatus) -> None: ...
