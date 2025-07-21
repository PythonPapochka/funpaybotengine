from __future__ import annotations

from funpaybotengine.dispatching.events.builtin_events import (
    NewSaleEvent,
    ChatInitEvent,
    NewMessageEvent,
    ChatChangedEvent,
    NewPurchaseEvent,
    SalesListChangedEvent,
    SaleStatusChangedEvent,
    PurchasesListChangedEvent,
    PurchaseStatusChangedEvent,
)
from funpaybotengine.dispatching.handlers.handler_manager import HandlerManager


class Router:
    def __init__(self, router_id: str) -> None:
        self._id = router_id
        self._parent_router: Router | None = None
        self._inner_routers: dict[str, Router] = {}

        self.on_chat_init_event = HandlerManager(event_type=ChatInitEvent)
        self.on_chat_changed_event = HandlerManager(event_type=ChatChangedEvent)
        self.on_new_message_event = HandlerManager(event_type=NewMessageEvent)
        self.on_sales_list_changed_event = HandlerManager(event_type=SalesListChangedEvent)
        self.on_new_sale_event = HandlerManager(event_type=NewSaleEvent)
        self.on_sale_status_changed_event = HandlerManager(event_type=SaleStatusChangedEvent)
        self.on_purchases_list_changed_event = HandlerManager(event_type=PurchasesListChangedEvent)
        self.on_new_purchase_event = HandlerManager(event_type=NewPurchaseEvent)
        self.on_purchase_status_changed_event = HandlerManager(
            event_type=PurchaseStatusChangedEvent
        )
        self.on_event = HandlerManager()

    def connect_router(self, router: Router) -> None:
        if router.parent_router is not None:
            raise Exception('Router is already connected to ...')  # todo: exception

        if router is self:
            raise Exception('Cannot connect self')  # todo: exception

        # if isinstance(router, 'RootRouter'):  # todo

        router._parent_router = self
        self._inner_routers[router.id] = router

    def connect_routers(self, *routers: Router) -> None:
        for i in routers:
            self.connect_router(i)

    @property
    def root_router(self) -> Router:
        if self.parent_router is None:
            return self
        return self.parent_router.root_router

    @property
    def parent_router(self) -> Router | None:
        return self._parent_router

    @property
    def id(self) -> str:
        return self._id
