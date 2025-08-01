from __future__ import annotations


__all__ = (
    'ChatInitEvent',
    'ChatChangedEvent',
    'NewMessageEvent',
    'CountersChangedEvent',
    'NewSaleEvent',
    'SaleStatusChangedEvent',
    'NewPurchaseEvent',
    'PurchaseStatusChangedEvent',
)


from funpaybotengine.types.chat import PrivateChatPreview
from funpaybotengine.types.orders import OrderPreview
from funpaybotengine.types.messages import Message

from .base import RunnerEvent


class ChatInitEvent(RunnerEvent[PrivateChatPreview]): ...


class ChatChangedEvent(RunnerEvent[PrivateChatPreview]):
    previous: PrivateChatPreview | None = None


class NewMessageEvent(RunnerEvent[Message]): ...


class CountersChangedEvent(RunnerEvent[tuple[int, int]]): ...


class NewSaleEvent(RunnerEvent[OrderPreview]):
    related_system_message: NewMessageEvent | None = None
    related_auto_messages: list[NewMessageEvent] = []


class SaleStatusChangedEvent(RunnerEvent[OrderPreview]):
    previous: OrderPreview | None = None
    related_system_message: NewMessageEvent | None = None


class NewPurchaseEvent(RunnerEvent[OrderPreview]):
    related_system_message: NewMessageEvent | None = None
    related_auto_messages: list[NewMessageEvent] = []

class PurchaseStatusChangedEvent(RunnerEvent[OrderPreview]):
    previous: OrderPreview | None = None
    related_system_message: NewMessageEvent | None = None
