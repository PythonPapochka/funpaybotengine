from __future__ import annotations


__all__ = ['Router']


from eventry.asyncio.router import Router as BaseRouter

from funpaybotengine.dispatching.events.base import ExceptionEvent
from funpaybotengine.dispatching.events.builtin_events import (
    NewSaleEvent,
    NewMessageEvent,
    SaleClosedEvent,
    ChatChangedEvent,
    NewPurchaseEvent,
    SaleRefundedEvent,
    SaleReopenedEvent,
    PurchaseClosedEvent,
    CountersChangedEvent,
    PurchaseRefundedEvent,
    PurchaseReopenedEvent,
    SaleClosedByAdminEvent,
    SaleStatusChangedEvent,
    PurchaseClosedByAdminEvent,
    PurchaseStatusChangedEvent,
    SalePartiallyRefundedEvent,
    PurchasePartiallyRefundedEvent,
)
from funpaybotengine.dispatching.handlers.handler_manager import HandlerManager


_events = {
    'chat_changed': ChatChangedEvent,
    'new_message': NewMessageEvent,
    'counters_changed': CountersChangedEvent,
    'new_sale': NewSaleEvent,
    'sale_closed_by_admin': SaleClosedByAdminEvent,
    'sale_closed': SaleClosedEvent,
    'sale_partially_refunded': SalePartiallyRefundedEvent,
    'sale_refunded': SaleRefundedEvent,
    'sale_reopened': SaleReopenedEvent,
    'sale_status_changed': SaleStatusChangedEvent,
    'new_purchase': NewPurchaseEvent,
    'purchase_closed_by_admin': PurchaseClosedByAdminEvent,
    'purchase_closed': PurchaseClosedEvent,
    'purchase_partially_refunded': PurchasePartiallyRefundedEvent,
    'purchase_refunded': PurchaseRefundedEvent,
    'purchase_reopened': PurchaseReopenedEvent,
    'purchase_status_changed': PurchaseStatusChangedEvent,
    'exception': ExceptionEvent,
}


class Router(BaseRouter):
    on_chat_changed: HandlerManager
    on_new_message: HandlerManager
    on_counters_changed: HandlerManager
    on_new_sale: HandlerManager
    on_sale_status_changed: HandlerManager
    on_sale_closed: HandlerManager
    on_sale_closed_by_admin: HandlerManager
    on_sale_refunded: HandlerManager
    on_sale_partially_refunded: HandlerManager
    on_sale_reopened: HandlerManager
    on_new_purchase: HandlerManager
    on_purchase_status_changed: HandlerManager
    on_purchase_closed: HandlerManager
    on_purchase_closed_by_admin: HandlerManager
    on_purchase_refunded: HandlerManager
    on_purchase_partially_refunded: HandlerManager
    on_purchase_reopened: HandlerManager
    on_event: HandlerManager

    def __init__(self, router_id: str | None = None) -> None:
        super().__init__(router_id=router_id or f'Router{id(self)}')
        self._default_handler_manager = HandlerManager(self, 'default', None)

        for name, event in _events.items():
            manager = self._add_handler_manager(HandlerManager(self, name, event))  # type: ignore
            setattr(self, f'on_{name}', manager)

        setattr(self, 'on_event', property(lambda s: s._default_handler_manager))
