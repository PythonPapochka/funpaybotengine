from __future__ import annotations


__all__ = ('Router',)

from typing import TYPE_CHECKING, Any, Type, Generator, AsyncGenerator

from funpaybotengine.loggers import router_logger
from funpaybotengine.dispatching.events.base import Event, ExceptionEvent
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


if TYPE_CHECKING:
    from funpaybotengine.dispatching.bases import HandlerInfo


class Router:
    def __init__(self, name: str | None = None) -> None:
        self._name = name or f'Router{id(self)}'
        self._parent_router: Router | None = None
        self._inner_routers: dict[str, Router] = {}

        self._managers: dict[Type[Event[Any]], HandlerManager[Any]] = {
            ChatChangedEvent: HandlerManager(self, 'chat_changed', ChatChangedEvent),
            NewMessageEvent: HandlerManager(self, 'new_message', NewMessageEvent),
            CountersChangedEvent: HandlerManager(self, 'counters_changed', CountersChangedEvent),
            NewSaleEvent: HandlerManager(self, 'new_sale', NewSaleEvent),
            SaleClosedByAdminEvent: HandlerManager(
                self,
                'sale_closed_by_admin',
                SaleClosedByAdminEvent,
            ),
            SaleClosedEvent: HandlerManager(self, 'sale_closed', SaleClosedEvent),
            SalePartiallyRefundedEvent: HandlerManager(
                self, 'sale_partially_refunded', SalePartiallyRefundedEvent,
            ),
            SaleRefundedEvent: HandlerManager(self, 'sale_refunded', SaleRefundedEvent),
            SaleReopenedEvent: HandlerManager(self, 'sale_reopened', SaleReopenedEvent),
            SaleStatusChangedEvent: HandlerManager(
                self,
                'sale_status_changed',
                SaleStatusChangedEvent,
            ),
            NewPurchaseEvent: HandlerManager(self, 'new_purchase', NewPurchaseEvent),
            PurchaseClosedByAdminEvent: HandlerManager(
                self, 'sale_closed_by_admin', PurchaseClosedByAdminEvent,
            ),
            PurchaseClosedEvent: HandlerManager(self, 'sale_closed', PurchaseClosedEvent),
            PurchasePartiallyRefundedEvent: HandlerManager(
                self, 'sale_partially_refunded', PurchasePartiallyRefundedEvent,
            ),
            PurchaseRefundedEvent: HandlerManager(self, 'sale_refunded', PurchaseRefundedEvent),
            PurchaseReopenedEvent: HandlerManager(self, 'sale_reopened', PurchaseReopenedEvent),
            PurchaseStatusChangedEvent: HandlerManager(
                self,
                'purchase_status_changed',
                PurchaseStatusChangedEvent,
            ),
            ExceptionEvent: HandlerManager(self, 'on_exception', ExceptionEvent),
            Event: HandlerManager(self, 'on_event'),
        }

    def connect_router(self, router: Router) -> None:
        router.parent_router = self

    def connect_routers(self, *routers: Router) -> None:
        for i in routers:
            self.connect_router(i)

    def get_handler_by_id(self, handler_id: str, /) -> HandlerInfo | None:
        for manager in self._managers.values():
            try:
                return manager.handlers[handler_id]
            except KeyError:
                continue

        for router in self._inner_routers.values():
            result = router.get_handler_by_id(handler_id)
            if result is not None:
                return result
        return None

    async def get_matching_handlers(
        self,
        event: Event[Any],
        workflow_data: dict[str, Any],
    ) -> AsyncGenerator[tuple[HandlerInfo, Exception | None], None]:
        manager = self.get_manager_by_event(event)

        async for handler, e in manager.get_matching_handlers(event, workflow_data):
            yield handler, e

        for router in self._inner_routers.values():
            async for handler, e in router.get_matching_handlers(event, workflow_data):
                yield handler, e

    def get_manager_by_event(self, event: Event[Any]) -> HandlerManager[Any]:
        for t, m in self._managers.items():
            if isinstance(event, t):
                return m
        return self.on_event

    @property
    def on_chat_changed(self) -> HandlerManager[ChatChangedEvent]:
        return self._managers[ChatChangedEvent]

    @property
    def on_new_message(self) -> HandlerManager[NewMessageEvent]:
        return self._managers[NewMessageEvent]

    @property
    def on_orders_counters_changed(self) -> HandlerManager[CountersChangedEvent]:
        return self._managers[CountersChangedEvent]

    @property
    def on_new_sale(self) -> HandlerManager[NewSaleEvent]:
        return self._managers[NewSaleEvent]

    @property
    def on_sale_status_changed(self) -> HandlerManager[SaleStatusChangedEvent]:
        return self._managers[SaleStatusChangedEvent]

    @property
    def on_sale_closed(self) -> HandlerManager[SaleClosedEvent]:
        return self._managers[SaleClosedEvent]

    @property
    def on_sale_closed_by_admin(self) -> HandlerManager[SaleClosedByAdminEvent]:
        return self._managers[SaleClosedByAdminEvent]

    @property
    def on_sale_refunded(self) -> HandlerManager[SaleRefundedEvent]:
        return self._managers[SaleRefundedEvent]

    @property
    def on_sale_partially_refunded(self) -> HandlerManager[SalePartiallyRefundedEvent]:
        return self._managers[SalePartiallyRefundedEvent]

    @property
    def on_sale_reopened(self) -> HandlerManager[SaleReopenedEvent]:
        return self._managers[SaleReopenedEvent]

    @property
    def on_new_purchase(self) -> HandlerManager[NewPurchaseEvent]:
        return self._managers[NewPurchaseEvent]

    @property
    def on_purchase_status_changed(self) -> HandlerManager[PurchaseStatusChangedEvent]:
        return self._managers[PurchaseStatusChangedEvent]

    @property
    def on_purchase_closed(self) -> HandlerManager[PurchaseClosedEvent]:
        return self._managers[PurchaseClosedEvent]

    @property
    def on_purchase_closed_by_admin(self) -> HandlerManager[PurchaseClosedByAdminEvent]:
        return self._managers[PurchaseClosedByAdminEvent]

    @property
    def on_purchase_refunded(self) -> HandlerManager[PurchaseRefundedEvent]:
        return self._managers[PurchaseRefundedEvent]

    @property
    def on_purchase_partially_refunded(self) -> HandlerManager[PurchasePartiallyRefundedEvent]:
        return self._managers[PurchasePartiallyRefundedEvent]

    @property
    def on_purchase_reopened(self) -> HandlerManager[PurchaseReopenedEvent]:
        return self._managers[SaleReopenedEvent]

    @property
    def on_event(self) -> HandlerManager[Event[Any]]:
        return self._managers[Event]

    @property
    def root_router(self) -> Router:
        if self.parent_router is None:
            return self
        return self.parent_router.root_router

    @property
    def chain_to_root_router(self) -> Generator[Router, None, None]:
        curr_router: Router | None = self
        while curr_router is not None:
            yield curr_router
            curr_router = curr_router.parent_router

    @property
    def chain_to_last_router(self) -> Generator[Router, None, None]:
        yield self
        for r in self._inner_routers.values():
            yield from r.chain_to_last_router

    @property
    def parent_router(self) -> Router | None:
        return self._parent_router

    @parent_router.setter
    def parent_router(self, router: Router) -> None:
        if self.parent_router:
            raise RuntimeError(
                f"Router '{self.name}' is already connected to router "
                f"'{self.parent_router.name}'.",
            )

        if not isinstance(router, Router):
            raise ValueError(
                f'Router should be an instance of Router, not {type(router).__name__!r}',
            )

        if router is self:
            raise RuntimeError(
                'Cannot connect router to itself.',
            )

        for i in router.chain_to_root_router:
            if i.parent_router is self:
                raise RuntimeError('Circular connection of routers is not allowed.')  # todo: tree

        # todo: add name check

        self._parent_router = router
        router._inner_routers[self.name] = self
        router_logger.info(
            f"Router '{self.name}' connected to router '{router.name}'.",
        )

    @property
    def name(self) -> str:
        return self._name
