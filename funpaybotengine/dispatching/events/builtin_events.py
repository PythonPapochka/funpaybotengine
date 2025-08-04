from __future__ import annotations


__all__ = (
    'ChatInitEvent',
    'ChatChangedEvent',
    'NewMessageEvent',
    'CountersChangedEvent',
    'OrderEvent',
    'NewSaleEvent',
    'SaleStatusChangedEvent',
    'SaleClosedEvent',
    'SaleClosedByAdminEvent',
    'SaleRefundedEvent',
    'SalePartiallyRefundedEvent',
    'SaleReopenedEvent',
    'SaleStatusChangedEvent',
    'NewPurchaseEvent',
    'PurchaseStatusChangedEvent',
    'PurchaseClosedEvent',
    'PurchaseClosedByAdminEvent',
    'PurchaseRefundedEvent',
    'PurchasePartiallyRefundedEvent',
    'PurchaseReopenedEvent',
)


from pydantic import Field, PrivateAttr

from funpaybotengine.types.chat import PrivateChatPreview
from funpaybotengine.types.orders import OrderPreview
from funpaybotengine.types.messages import Message

from .base import RunnerEvent


class ChatInitEvent(RunnerEvent[PrivateChatPreview]): ...


class ChatChangedEvent(RunnerEvent[PrivateChatPreview]):
    previous: PrivateChatPreview | None = None


class NewMessageEvent(RunnerEvent[Message]): ...


class CountersChangedEvent(RunnerEvent[tuple[int, int]]): ...


class OrderEvent(RunnerEvent[Message]):
    related_new_message_event: NewMessageEvent
    _order_preview: OrderPreview | None = PrivateAttr(default=None)

    async def get_order_preview(self, update: bool = False) -> OrderPreview:
        if self._order_preview is not None and not update:
            return self._order_preview

        assert self.bot is not None, 'Event not bound to any bot.'

        return (await self.bot.get_sales(order_id_filter=self.object.meta.order_id)).orders[0]


class NewSaleEvent(OrderEvent):
    related_auto_message_events: list[NewMessageEvent] = Field(default_factory=list)


class SaleStatusChangedEvent(OrderEvent):
    previous: OrderPreview | None = None


class SaleClosedEvent(SaleStatusChangedEvent): ...


class SaleClosedByAdminEvent(SaleClosedEvent): ...


class SaleRefundedEvent(SaleStatusChangedEvent): ...


class SalePartiallyRefundedEvent(SaleRefundedEvent): ...


class SaleReopenedEvent(SaleStatusChangedEvent): ...


class NewPurchaseEvent(OrderEvent):
    related_auto_message_events: list[NewMessageEvent] = Field(default_factory=list)


class PurchaseStatusChangedEvent(OrderEvent):
    previous: OrderPreview | None = None


class PurchaseClosedEvent(PurchaseStatusChangedEvent): ...


class PurchaseClosedByAdminEvent(PurchaseClosedEvent): ...


class PurchaseRefundedEvent(PurchaseStatusChangedEvent): ...


class PurchasePartiallyRefundedEvent(PurchaseRefundedEvent): ...


class PurchaseReopenedEvent(PurchaseStatusChangedEvent): ...
