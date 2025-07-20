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

from .base import RunnerEvent
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from funpaybotengine.types.messages import Message
    from funpaybotengine.types.chat import PrivateChatPreview
    from funpaybotengine.types.orders import OrderPreview


class ChatInitEvent(RunnerEvent[PrivateChatPreview]):
    ...


class ChatChangedEvent(RunnerEvent[PrivateChatPreview]):
    ...


class NewMessageEvent(RunnerEvent[Message]):
    ...


class SalesListChangedEvent(RunnerEvent[int]):
    ...


class NewSaleEvent(RunnerEvent[OrderPreview]):
    ...


class SaleStatusChangedEvent(RunnerEvent[OrderPreview]):
    ...


class PurchasesListChangedEvent(RunnerEvent[int]):
    ...


class NewPurchaseEvent(RunnerEvent[OrderPreview]):
    ...


class PurchaseStatusChangedEvent(RunnerEvent[OrderPreview]):
    ...
