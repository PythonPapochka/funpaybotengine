from __future__ import annotations


__all__ = ('Router',)

from typing import TYPE_CHECKING, Any, Type, Generator, AsyncGenerator

from funpaybotengine.loggers import router_logger
from funpaybotengine.dispatching.events.base import Event, ExceptionEvent
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


if TYPE_CHECKING:
    from funpaybotengine.dispatching.bases import HandlerInfo


class Router:
    def __init__(self, name: str | None = None) -> None:
        self._name = name or f'Router{id(self)}'
        self._parent_router: Router | None = None
        self._inner_routers: dict[str, Router] = {}

        self._on_chat_init_event = HandlerManager(
            self,
            name='on_chat_init',
            event_type_filter=ChatInitEvent,
        )
        self._on_chat_changed_event = HandlerManager(
            self,
            name='on_chat_changed',
            event_type_filter=ChatChangedEvent,
        )
        self._on_new_message_event = HandlerManager(
            self,
            name='on_new_message',
            event_type_filter=NewMessageEvent,
        )
        self._on_sales_list_changed_event = HandlerManager(
            self,
            name='on_sales_list_changed',
            event_type_filter=SalesListChangedEvent,
        )
        self._on_new_sale_event = HandlerManager(
            self,
            name='on_new_sale',
            event_type_filter=NewSaleEvent,
        )
        self._on_sale_status_changed_event = HandlerManager(
            self,
            name='on_sale_status_changed',
            event_type_filter=SaleStatusChangedEvent,
        )
        self._on_purchases_list_changed_event = HandlerManager(
            self,
            name='on_purchases_list_changed',
            event_type_filter=PurchasesListChangedEvent,
        )
        self._on_new_purchase_event = HandlerManager(
            self,
            name='on_new_purchase',
            event_type_filter=NewPurchaseEvent,
        )
        self._on_purchase_status_changed_event = HandlerManager(
            self,
            name='on_purchase_status_changed',
            event_type_filter=PurchaseStatusChangedEvent,
        )
        self._on_exception = HandlerManager(
            self,
            name='on_exception',
            event_type_filter=ExceptionEvent,
        )
        self._on_event: HandlerManager[Event[Any]] = HandlerManager(
            self,
            name='on_event',
        )

        self._managers: dict[Type[Event[Any]], HandlerManager[Any]] = {
            ChatInitEvent: self._on_chat_init_event,
            ChatChangedEvent: self._on_chat_changed_event,
            NewMessageEvent: self._on_new_message_event,
            SalesListChangedEvent: self._on_sales_list_changed_event,
            NewSaleEvent: self._on_new_sale_event,
            SaleStatusChangedEvent: self._on_sale_status_changed_event,
            PurchasesListChangedEvent: self._on_purchases_list_changed_event,
            NewPurchaseEvent: self._on_new_purchase_event,
            PurchaseStatusChangedEvent: self._on_purchase_status_changed_event,
            ExceptionEvent: self._on_exception,
            Event: self._on_event,
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
    ) -> AsyncGenerator[HandlerInfo, None]:
        manager = self._managers.get(type(event)) or self._on_event
        async for handler in manager.get_matching_handlers(event, workflow_data):
            yield handler

        for router in self._inner_routers.values():
            async for handler in router.get_matching_handlers(event, workflow_data):
                yield handler

    def get_manager_by_event(self, event: Event[Any] | Type[Event[Any]]) -> HandlerManager[Any]:
        filter = event if isinstance(event, type) else type(event)
        return self._managers.get(filter) or self._on_event

    @property
    def on_init_chat_event(self) -> HandlerManager[ChatInitEvent]:
        return self._on_chat_init_event

    @property
    def on_chat_changed_event(self) -> HandlerManager[ChatChangedEvent]:
        return self._on_chat_changed_event

    @property
    def on_new_message_event(self) -> HandlerManager[NewMessageEvent]:
        return self._on_new_message_event

    @property
    def on_sales_list_changed_event(self) -> HandlerManager[SalesListChangedEvent]:
        return self._on_sales_list_changed_event

    @property
    def on_new_sale_event(self) -> HandlerManager[NewSaleEvent]:
        return self._on_new_sale_event

    @property
    def on_sale_status_changed_event(self) -> HandlerManager[SaleStatusChangedEvent]:
        return self._on_sale_status_changed_event

    @property
    def on_purchases_list_changed_event(self) -> HandlerManager[PurchasesListChangedEvent]:
        return self._on_purchases_list_changed_event

    @property
    def on_new_purchase_event(self) -> HandlerManager[NewPurchaseEvent]:
        return self._on_new_purchase_event

    @property
    def on_purchase_status_changed_event(self) -> HandlerManager[PurchaseStatusChangedEvent]:
        return self._on_purchase_status_changed_event

    @property
    def on_event(self) -> HandlerManager[Event[Any]]:
        return self._on_event

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
            f"Router '{self.name}' connected to router '{self.parent_router.name}'.",
        )

    @property
    def name(self) -> str:
        return self._name
