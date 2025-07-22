from __future__ import annotations


__all__ = (
    'ChatInitEvent',
    'ChatChangedEvent',
    'NewMessageEvent',
    'SalesListChangedEvent',
    'NewSaleEvent',
    'SaleStatusChangedEvent',
    'PurchasesListChangedEvent',
    'NewPurchaseEvent',
    'PurchaseStatusChangedEvent',
)


from funpaybotengine.types.chat import PrivateChatPreview
from funpaybotengine.types.orders import OrderPreview
from funpaybotengine.types.messages import Message

from .base import RunnerEvent


class ChatInitEvent(RunnerEvent[PrivateChatPreview]): ...


class ChatChangedEvent(RunnerEvent[PrivateChatPreview]): ...


class NewMessageEvent(RunnerEvent[Message]):
    def __init__(self, obj: Message, tag: str) -> None:
        super().__init__(obj=obj, tag=tag)


class SalesListChangedEvent(RunnerEvent[int]): ...


class NewSaleEvent(RunnerEvent[OrderPreview]): ...


class SaleStatusChangedEvent(RunnerEvent[OrderPreview]): ...


class PurchasesListChangedEvent(RunnerEvent[int]): ...


class NewPurchaseEvent(RunnerEvent[OrderPreview]): ...


class PurchaseStatusChangedEvent(RunnerEvent[OrderPreview]): ...
