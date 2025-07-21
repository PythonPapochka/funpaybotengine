from __future__ import annotations

from typing import Any, Generic, TypeVar, Generator
from collections.abc import Mapping

from funpaybotengine.dispatching.events.base import Event
from funpaybotengine.dispatching.handlers.handler import Handler
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


KT = TypeVar('KT', bound=Any)
VT = TypeVar('VT', bound=Any)


class ReadOnlyChainMap(Generic[KT, VT]):
    def __init__(self, *mappings: Mapping[KT, VT]) -> None:
        self._mappings = mappings
        super().__init__()

    def __getitem__(self, key: KT) -> VT:
        for i in self._mappings:
            try:
                return i[key]
            except KeyError:
                continue
        raise KeyError

    def get(self, key: KT) -> VT | None:
        for i in self._mappings:
            try:
                return i[key]
            except KeyError:
                continue
        return None


class Router:
    def __init__(self, router_id: str) -> None:
        self._id = router_id
        self._parent_router: Router | None = None
        self._inner_routers: dict[str, Router] = {}

        self.on_chat_init_event = HandlerManager(self, event_type=ChatInitEvent)
        self.on_chat_changed_event = HandlerManager(self, event_type=ChatChangedEvent)
        self.on_new_message_event = HandlerManager(self, event_type=NewMessageEvent)
        self.on_sales_list_changed_event = HandlerManager(self, event_type=SalesListChangedEvent)
        self.on_new_sale_event = HandlerManager(self, event_type=NewSaleEvent)
        self.on_sale_status_changed_event = HandlerManager(self, event_type=SaleStatusChangedEvent)
        self.on_purchases_list_changed_event = HandlerManager(
            self, event_type=PurchasesListChangedEvent
        )
        self.on_new_purchase_event = HandlerManager(self, event_type=NewPurchaseEvent)
        self.on_purchase_status_changed_event = HandlerManager(
            self, event_type=PurchaseStatusChangedEvent
        )
        self.on_event = HandlerManager(self)

        self.managers = {
            ChatInitEvent: self.on_chat_init_event,
            ChatChangedEvent: self.on_chat_changed_event,
            NewMessageEvent: self.on_new_message_event,
            SalesListChangedEvent: self.on_sales_list_changed_event,
            NewSaleEvent: self.on_sale_status_changed_event,
            SaleStatusChangedEvent: self.on_sale_status_changed_event,
            PurchasesListChangedEvent: self.on_purchases_list_changed_event,
            NewPurchaseEvent: self.on_purchase_status_changed_event,
            PurchaseStatusChangedEvent: self.on_purchase_status_changed_event,
            Event: self.on_event,
        }

        self.handlers: ReadOnlyChainMap[str, Handler] = ReadOnlyChainMap(
            *[i._handlers for i in self.managers.values()]
        )

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

    @property
    def id(self) -> str:
        return self._id
