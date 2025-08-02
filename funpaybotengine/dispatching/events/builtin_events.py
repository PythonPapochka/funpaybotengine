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
from pydantic import PrivateAttr
from funpaybotengine.types.messages import Message
from typing import Any

from .base import RunnerEvent


class ChatInitEvent(RunnerEvent[PrivateChatPreview]): ...


class ChatChangedEvent(RunnerEvent[PrivateChatPreview]):
    previous: PrivateChatPreview | None = None


class NewMessageEvent(RunnerEvent[Message]): ...


class CountersChangedEvent(RunnerEvent[tuple[int, int]]): ...


class OrderEvent(RunnerEvent[Message]):
    _order_preview: OrderPreview | None = PrivateAttr(default=None)

    def __post_init__(self, context: dict[Any, Any]) -> None:
        self._order_preview = context.get("order_preview")

    async def get_order_preview(self, update: bool = False) -> OrderPreview:
        if self._order_preview is not None and not update:
            return self._order_preview

        assert self.bot is not None, 'Event not bound to any bot.'

        return (await self.bot.get_sales(order_id_filter=self.object.meta.order_id)).orders[0]


class NewSaleEvent(OrderEvent): ...


class SaleStatusChangedEvent(OrderEvent): ...


class SaleClosedEvent(SaleStatusChangedEvent): ...


class SaleClosedByAdminEvent(SaleClosedEvent): ...


class SaleRefundedEvent(SaleStatusChangedEvent): ...


class SalePartiallyRefundedEvent(SaleRefundedEvent): ...


class SaleReopenedEvent(SaleStatusChangedEvent): ...


class NewPurchaseEvent(OrderEvent): ...


class PurchaseStatusChangedEvent(OrderEvent): ...


class PurchaseClosedEvent(PurchaseStatusChangedEvent): ...


class PurchaseClosedByAdminEvent(PurchaseClosedEvent): ...


class PurchaseRefundedEvent(PurchaseStatusChangedEvent): ...


class PurchasePartiallyRefundedEvent(PurchaseRefundedEvent): ...


class PurchaseReopenedEvent(PurchaseStatusChangedEvent): ...