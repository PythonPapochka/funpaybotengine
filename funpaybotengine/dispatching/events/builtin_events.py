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


from typing import Any

from pydantic import Field, PrivateAttr

from funpaybotengine.types.chat import PrivateChatPreview
from funpaybotengine.types.orders import OrderPreview
from funpaybotengine.types.messages import Message

from .base import RunnerEvent


class ChatInitEvent(RunnerEvent[PrivateChatPreview]):
    @property
    def chat_preview(self) -> PrivateChatPreview:
        return self.object

    @property
    def workflow_dict(self) -> dict[str, Any]:
        return {
            'chat_preview': self.chat_preview,
        }


class ChatChangedEvent(RunnerEvent[PrivateChatPreview]):
    previous: PrivateChatPreview | None = None

    @property
    def chat_preview(self) -> PrivateChatPreview:
        return self.object

    @property
    def workflow_dict(self) -> dict[str, Any]:
        return {
            'chat_preview': self.chat_preview,
        }


class NewMessageEvent(RunnerEvent[Message]):
    @property
    def message(self) -> Message:
        return self.object

    @property
    def workflow_dict(self) -> dict[str, Any]:
        return {
            'message': self.message,
        }


class CountersChangedEvent(RunnerEvent[tuple[int, int]]):
    @property
    def sales_counters(self) -> int:
        return self.object[0]

    @property
    def purchases_counters(self) -> int:
        return self.object[1]

    @property
    def workflow_dict(self) -> dict[str, Any]:
        return {
            'sales_counter': self.sales_counters,
            'purchases_counter': self.purchases_counters,
        }


class OrderEvent(RunnerEvent[Message]):
    related_new_message_event: NewMessageEvent
    _order_preview: OrderPreview | None = PrivateAttr(default=None)

    @property
    def message(self) -> Message:
        return self.object

    @property
    def workflow_dict(self) -> dict[str, Any]:
        return {
            'message': self.message,
            'new_message_event': self.related_new_message_event,
        }


class SaleEvent(OrderEvent):
    async def get_order_preview(self, update: bool = False) -> OrderPreview:
        if self._order_preview is not None and not update:
            return self._order_preview

        orders = await self.get_bound_bot().get_sales(order_id_filter=self.object.meta.order_id)
        return orders.orders[0]


class PurchaseEvent(OrderEvent):
    async def get_order_preview(self, update: bool = False) -> OrderPreview:
        if self._order_preview is not None and not update:
            return self._order_preview

        orders = await self.get_bound_bot().get_purchases(
            order_id_filter=self.object.meta.order_id,
        )
        return orders.orders[0]


class NewSaleEvent(SaleEvent):
    related_auto_message_events: list[NewMessageEvent] = Field(default_factory=list)


class SaleStatusChangedEvent(SaleEvent):
    previous: OrderPreview | None = None


class SaleClosedEvent(SaleStatusChangedEvent): ...


class SaleClosedByAdminEvent(SaleClosedEvent): ...


class SaleRefundedEvent(SaleStatusChangedEvent): ...


class SalePartiallyRefundedEvent(SaleRefundedEvent): ...


class SaleReopenedEvent(SaleStatusChangedEvent): ...


class NewPurchaseEvent(PurchaseEvent):
    related_auto_message_events: list[NewMessageEvent] = Field(default_factory=list)


class PurchaseStatusChangedEvent(PurchaseEvent):
    previous: OrderPreview | None = None


class PurchaseClosedEvent(PurchaseStatusChangedEvent): ...


class PurchaseClosedByAdminEvent(PurchaseClosedEvent): ...


class PurchaseRefundedEvent(PurchaseStatusChangedEvent): ...


class PurchasePartiallyRefundedEvent(PurchaseRefundedEvent): ...


class PurchaseReopenedEvent(PurchaseStatusChangedEvent): ...
