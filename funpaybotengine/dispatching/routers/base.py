from __future__ import annotations


__all__ = ['Router']


from typing import cast

from eventry.asyncio.router import Router as BaseRouter

from funpaybotengine.dispatching import events
from funpaybotengine.dispatching.handlers.handler_manager import HandlerManager


class Router(BaseRouter):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name=name or f'Router{id(self)}')
        self.set_default_handler_manager(HandlerManager(self, 'default', None))

        self.on_chat_changed = self._add_handler_manager(
            HandlerManager(self, 'on_chat_changed', events.ChatChangedEvent.__event_name__)
        )
        self.on_new_message = self._add_handler_manager(
            HandlerManager(self, 'on_new_message', events.NewMessageEvent.__event_name__)
        )
        self.on_new_sale = self._add_handler_manager(
            HandlerManager(self, 'on_new_sale', events.NewSaleEvent.__event_name__)
        )
        self.on_sale_status_changed = self._add_handler_manager(
            HandlerManager(
                self, 'on_sale_status_changed', events.SaleStatusChangedEvent.__event_name__
            )
        )
        self.on_sale_closed = self._add_handler_manager(
            HandlerManager(self, 'on_sale_closed', events.SaleClosedEvent.__event_name__)
        )
        self.on_sale_closed_by_admin = self._add_handler_manager(
            HandlerManager(
                self, 'on_sale_closed_by_admin', events.SaleClosedByAdminEvent.__event_name__
            )
        )
        self.on_sale_refunded = self._add_handler_manager(
            HandlerManager(self, 'on_sale_refunded', events.SaleRefundedEvent.__event_name__)
        )
        self.on_sale_partially_refunded = self._add_handler_manager(
            HandlerManager(
                self,
                'on_sale_partially_refunded',
                events.SalePartiallyRefundedEvent.__event_name__,
            )
        )
        self.on_sale_reopened = self._add_handler_manager(
            HandlerManager(self, 'on_sale_reopened', events.SaleReopenedEvent.__event_name__)
        )
        self.on_new_purchase = self._add_handler_manager(
            HandlerManager(self, 'on_new_purchase', events.NewPurchaseEvent.__event_name__)
        )
        self.on_purchase_status_changed = self._add_handler_manager(
            HandlerManager(
                self,
                'on_purchase_status_changed',
                events.PurchaseStatusChangedEvent.__event_name__,
            )
        )
        self.on_purchase_closed = self._add_handler_manager(
            HandlerManager(self, 'on_purchase_closed', events.PurchaseClosedEvent.__event_name__)
        )
        self.on_purchase_closed_by_admin = self._add_handler_manager(
            HandlerManager(
                self,
                'on_purchase_closed_by_admin',
                events.PurchaseClosedByAdminEvent.__event_name__,
            )
        )
        self.on_purchase_refunded = self._add_handler_manager(
            HandlerManager(
                self, 'on_purchase_refunded', events.PurchaseRefundedEvent.__event_name__
            )
        )
        self.on_purchase_partially_refunded = self._add_handler_manager(
            HandlerManager(
                self,
                'on_purchase_partially_refunded',
                events.PurchasePartiallyRefundedEvent.__event_name__,
            )
        )
        self.on_purchase_reopened = self._add_handler_manager(
            HandlerManager(
                self, 'on_purchase_reopened', events.PurchaseReopenedEvent.__event_name__
            )
        )
        self.on_new_review = self._add_handler_manager(
            HandlerManager(self, 'on_new_review', events.NewReviewEvent.__event_name__)
        )
        self.on_review_changed = self._add_handler_manager(
            HandlerManager(self, 'on_review_changed', events.ReviewChangedEvent.__event_name__)
        )
        self.on_review_deleted = self._add_handler_manager(
            HandlerManager(self, 'on_review_deleted', events.ReviewDeletedEvent.__event_name__)
        )
        self.on_new_review_response = self._add_handler_manager(
            HandlerManager(
                self, 'on_new_review_response', events.NewReviewResponseEvent.__event_name__
            )
        )
        self.on_review_response_changed = self._add_handler_manager(
            HandlerManager(
                self,
                'on_review_response_changed',
                events.ReviewResponseChangedEvent.__event_name__,
            )
        )
        self.on_review_response_deleted = self._add_handler_manager(
            HandlerManager(
                self,
                'on_review_response_deleted',
                events.ReviewResponseDeletedEvent.__event_name__,
            )
        )
        self.on_error = self._add_handler_manager(HandlerManager(self, 'on_error', 'error'))
        self.on_unauthenticated = self._add_handler_manager(
            HandlerManager(
                self, 'on_unauthenticated', events.BotUnauthenticatedEvent.__event_name__
            )
        )
        self.on_authenticated = self._add_handler_manager(
            HandlerManager(self, 'on_authenticated', events.BotAuthenticatedEvent.__event_name__)
        )
        self.on_new_events_pack = self._add_handler_manager(
            HandlerManager(self, 'on_new_events_pack', events.NewEventsPack.__event_name__)
        )

    @property
    def on_event(self) -> HandlerManager:
        return cast(HandlerManager, self._default_handler_manager)
