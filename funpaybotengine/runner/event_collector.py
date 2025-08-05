from __future__ import annotations


__all__ = ('EventCollector',)


from typing import TYPE_CHECKING, Type, Literal, TypeVar, Any
from dataclasses import field, dataclass
from collections import defaultdict
from collections.abc import Callable

from funpaybotengine.utils import random_runner_tag
from funpaybotengine.types.enums import MessageType, OrderPreviewType
from funpaybotengine.runner.config import RunnerConfig
from funpaybotengine.dispatching.events import (
    OrderEvent,
    NewSaleEvent,
    NewMessageEvent,
    SaleClosedEvent,
    ChatChangedEvent,
    NewPurchaseEvent,
    SaleRefundedEvent,
    SaleReopenedEvent,
    PurchaseClosedEvent,
    PurchaseRefundedEvent,
    PurchaseReopenedEvent,
    SaleClosedByAdminEvent,
    PurchaseClosedByAdminEvent,
    SalePartiallyRefundedEvent,
    PurchasePartiallyRefundedEvent,
)
from funpaybotengine.types.requests.runner import NodeRequestObject, ChatBookmarksRequestObject
from funpaybotengine.exceptions.session_exceptions import UnexpectedHTTPStatusError


if TYPE_CHECKING:
    from funpaybotengine.client.bot import Bot
    from funpaybotengine.types.orders import OrderPreview
    from funpaybotengine.types.updates import ChatNode, RunnerResponse, RunnerResponseObject


CHAT_EVENTS = ChatChangedEvent | NewMessageEvent

_ORDER_RELATED_MESSAGE_TYPES: dict[MessageType, tuple[Type[OrderEvent], Type[OrderEvent]]] = {
    MessageType.NEW_ORDER: (NewSaleEvent, NewPurchaseEvent),
    MessageType.ORDER_CLOSED: (SaleClosedEvent, PurchaseClosedEvent),
    MessageType.ORDER_CLOSED_BY_ADMIN: (SaleClosedByAdminEvent, PurchaseClosedByAdminEvent),
    MessageType.ORDER_REFUNDED: (SaleRefundedEvent, PurchaseRefundedEvent),
    MessageType.ORDER_PARTIALLY_REFUNDED: (
        SalePartiallyRefundedEvent,
        PurchasePartiallyRefundedEvent,
    ),
    MessageType.ORDER_REOPENED: (SaleReopenedEvent, PurchaseReopenedEvent),
}


F = TypeVar('F', bound=Callable[..., Any])


def attempts(amount: int = 0) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        async def inner(*args: Any, **kwargs: Any) -> Any:
            attempts = amount or float('inf')
            error: Exception = Exception()
            while attempts:
                attempts -= 1
                try:
                    return await func(*args, **kwargs)
                except UnexpectedHTTPStatusError as e:
                    error = e
            else:
                raise error
        return inner  # type: ignore
    return decorator



@dataclass
class OrderRelatedMessages:
    sales: list[NewMessageEvent] = field(default_factory=list)
    purchases: list[NewMessageEvent] = field(default_factory=list)
    unknown: list[NewMessageEvent] = field(default_factory=list)

    def add_event(
        self,
        event: NewMessageEvent,
        to: Literal['sales', 'purchases', 'unknown'],
    ) -> None:
        getattr(self, to).append(event)


class EventCollector:
    """
    Collects updates from FunPay and transforms them into update objects
    compatible with funpaybotengine.
    """

    def __init__(self, bot: Bot, config: RunnerConfig) -> None:
        self.bot = bot
        self.config = config

    @attempts()
    async def get_runner_updates(self) -> RunnerResponse:
        """
        Fetches the latest runner updates from FunPay.
        """
        chats = ChatBookmarksRequestObject(id=self.bot.userid, runner_tag=random_runner_tag())
        result = await self.bot.runner_request(requested_objects=[chats])
        return result

    @attempts()
    async def get_sales(self, order_id: str | None = None) -> tuple[OrderPreview, ...]:
        """
        Fetches last 100 sales from FunPay.

        If an order ID is provided, only the matching sale is returned.
        """
        return (await self.bot.get_sales(order_id_filter=order_id)).orders

    @attempts()
    async def get_purchases(self, order_id: str | None = None) -> tuple[OrderPreview, ...]:
        """
        Fetches last 100 purchases from FunPay.

        If an order ID is provided, only the matching purchase is returned.
        """
        return (await self.bot.get_purchases(order_id_filter=order_id)).orders

    async def get_nodes(self, chat_ids: list[int]) -> dict[int, RunnerResponseObject[ChatNode]]:
        nodes = {}
        objs = [NodeRequestObject(chat_id=i, runner_tag=random_runner_tag()) for i in chat_ids]

        for i in range(0, len(objs), 10):
            result = await self._get_nodes_inner(objs[i : i + 10])

            if result.nodes is None:
                raise Exception  # todo
            nodes.update({i.data.node.id: i for i in result.nodes})

        return nodes

    @attempts()
    async def _get_nodes_inner(self, objs: list[NodeRequestObject]) -> RunnerResponse:
        return await self.bot.runner_request(requested_objects=objs)

    async def get_chat_changed_events(self, runner_response: RunnerResponse) -> list[ChatChangedEvent]:
        if not runner_response.chat_bookmarks:
            return []

        result = []

        for chat_preview in reversed(runner_response.chat_bookmarks.data.chat_previews):
            cached_chat = await self.bot.session_storage.get_chat(chat_preview.id)

            if cached_chat == chat_preview:
                continue

            event = ChatChangedEvent(
                previous=cached_chat,
                object=chat_preview,
                tag=runner_response.chat_bookmarks.tag,
            ).as_(self.bot)

            result.append(event)

        return result

    async def get_new_message_events(self, events: list[ChatChangedEvent]) -> list[NewMessageEvent]:
        chat_changed_events = {e.object.id: e for e in events}
        nodes = await self.get_nodes([e.object.id for e in events])

        result: list[NewMessageEvent] = []
        for chat_id, event in chat_changed_events.items():
            node = nodes[chat_id]
            from_id = event.previous.last_message_id if event.previous else 0
            to_id = event.object.last_message_id

            result.extend(
                NewMessageEvent(object=message, tag=node.tag)
                for message in node.data.messages
                if from_id < message.id <= to_id
            )

        return result

    async def get_order_related_messages(self, events: list[NewMessageEvent]) -> OrderRelatedMessages:
        r = OrderRelatedMessages()
        for e in events:
            meta = e.object.meta
            if meta.type not in _ORDER_RELATED_MESSAGE_TYPES:
                continue

            if meta.buyer_id:
                r.sales.append(e) if meta.buyer_id == self.bot.userid else r.purchases.append(e)
            elif meta.seller_id:
                r.sales.append(e) if meta.seller_id == self.bot.userid else r.purchases.append(e)
            else:
                r.unknown.append(e)
        return r

    async def resolve_unknown_message(
            self,
            message: NewMessageEvent,
            messages: OrderRelatedMessages,
            sales: dict[str, OrderPreview],
            purchases: dict[str, OrderPreview],
    ) -> None:
        if message.object.meta.order_id in purchases:
            messages.purchases.append(message)
            return
        elif message.object.meta.order_id in sales:
            messages.sales.append(message)
            return

        saved_order = await self.bot.storage.get_order(message.object.meta.order_id) # type: ignore[arg-type]
        if saved_order and saved_order.type is not OrderPreviewType.UNKNOWN:
            if saved_order.type is OrderPreviewType.PURCHASE and self.config.discover_purchases:
                messages.purchases.append(message)
                purchases[saved_order.id] = saved_order
            elif saved_order.type is OrderPreviewType.SALE and self.config.discover_sales:
                messages.sales.append(message)
                sales[saved_order.id] = saved_order
            return

        if self.config.discover_purchases:
            order_preview = await self.get_purchases(order_id=message.object.meta.order_id)
            if order_preview:
                messages.purchases.append(message)
                purchases[order_preview[0].id] = order_preview[0]
                await self.bot.storage.update_order(order_preview[0])
                return

        if self.config.discover_sales:
            order_preview = await self.get_sales(order_id=message.object.meta.order_id)
            if order_preview:
                messages.sales.append(message)
                sales[order_preview[0].id] = order_preview[0]
                await self.bot.storage.update_order(order_preview[0])
                return

    async def make_order_events(self, messages: OrderRelatedMessages) -> list[OrderEvent]:
        sales, purchases = {}, {}
        total_events: list[OrderEvent] = []

        if messages.purchases or (messages.unknown and self.config.discover_purchases):
            purchases = {i.id: i for i in await self.get_purchases()}

        if messages.sales or (messages.unknown and self.config.discover_sales):
            sales = {i.id: i for i in await self.get_sales()}

        for e in messages.unknown:
            await self.resolve_unknown_message(e, messages, sales, purchases)

        total_events.extend(await self._make_order_events(messages.sales, sales, 'sales'))
        total_events.extend(await self._make_order_events(messages.purchases, purchases, 'purchases'))

        return total_events

    async def _make_order_events(
        self,
        messages: list[NewMessageEvent],
        orders: dict[str, OrderPreview],
        type: Literal['purchases', 'sales'],
    ) -> list[OrderEvent]:
        if not messages:
            return []

        result: list[OrderEvent] = []

        for e in messages:
            cls = _ORDER_RELATED_MESSAGE_TYPES[e.object.meta.type][0 if type == 'sales' else 1]
            event: OrderEvent = cls(object=e.object, related_new_message_event=e, tag=e.tag)
            event._order_preview = orders.get(e.object.meta.order_id)  # type: ignore[arg-type]
            result.append(event)

        return result

    async def get_order_events(self, events: list[NewMessageEvent]) -> list[OrderEvent]:
        order_messages = await self.get_order_related_messages(events=events)
        return await self.make_order_events(order_messages)

    def merge_events(
            self,
            chat_changed_events: list[ChatChangedEvent],
            new_message_events: list[NewMessageEvent],
            order_events: list[OrderEvent],
    ) -> list[CHAT_EVENTS | OrderEvent]:
        chat_id_to_messages: dict[int, list[NewMessageEvent]] = defaultdict(list)
        message_to_order: dict[NewMessageEvent, OrderEvent] = {}
        result: list[CHAT_EVENTS | OrderEvent] = []

        for i in new_message_events:
            chat_id_to_messages[i.object.chat_id].append(i)  # type: ignore[index]

        for j in order_events:
            message_to_order[j.related_new_message_event] = j

        for chat_changed_event in chat_changed_events:
            result.append(chat_changed_event)

            for new_message_event in chat_id_to_messages[chat_changed_event.object.id]:
                result.append(new_message_event)
                if message_to_order.get(new_message_event):
                    result.append(message_to_order[new_message_event])

        return result


    async def get_events(self) -> list[CHAT_EVENTS | OrderEvent]:
        runner_response = await self.get_runner_updates()
        chat_changed_events = await self.get_chat_changed_events(runner_response)
        new_message_events = await self.get_new_message_events(chat_changed_events)
        order_events = await self.get_order_events(new_message_events)
        total = self.merge_events(chat_changed_events, new_message_events, order_events)

        for i in chat_changed_events:
            await self.bot.session_storage.update_chat(i.object)

        order_events_mapping = {}
        for j in order_events:
            if j._order_preview is None:
                continue
            order_events_mapping[j._order_preview.id] = j._order_preview

        for k in order_events_mapping.values():
            await self.bot.storage.update_order(k)

        return total
