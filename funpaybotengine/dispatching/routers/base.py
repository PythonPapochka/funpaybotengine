from __future__ import annotations
from funpaybotengine.dispatching.handlers.handler_manager import HandlerManager


class Router:
    def __init__(self, router_id: str) -> None:
        self._id = router_id
        self._parent_router: Router | None = None
        self._inner_routers: dict[str, Router] = {}

        self.on_chat_init_event = HandlerManager()
        self.on_chat_changed_event = HandlerManager()
        self.on_new_message_event = HandlerManager()
        self.on_order_list_changed_event = HandlerManager()
        self.on_new_order_event = HandlerManager()
        self.on_order_status_changed_event = HandlerManager()

    def connect_router(self, router: Router) -> None:
        if router.parent_router is not None:
            raise Exception("Router is already connected to ...")  # todo: exception

        router._parent_router = self
        self._inner_routers[router.id] = router

    def connect_routers(self, *routers: Router) -> None:
        for i in routers:
            self.connect_router(i)

    @property
    def parent_router(self) -> Router | None:
        return self._parent_router

    @property
    def id(self) -> str:
        return self._id