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


class ChatChangedEvent(RunnerEvent[PrivateChatPreview]): ...


class NewMessageEvent(RunnerEvent[Message]): ...


class CountersChangedEvent(RunnerEvent[tuple[int, int]]): ...


class NewSaleEvent(RunnerEvent[OrderPreview]): ...


class SaleStatusChangedEvent(RunnerEvent[OrderPreview]): ...


class NewPurchaseEvent(RunnerEvent[OrderPreview]): ...


class PurchaseStatusChangedEvent(RunnerEvent[OrderPreview]): ...
