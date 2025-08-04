from __future__ import annotations


__all__ = ('EventCollector',)


from typing import TYPE_CHECKING, Type, Literal
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


if TYPE_CHECKING:
    from funpaybotengine.client.bot import Bot
    from funpaybotengine.types.orders import OrderPreview
    from funpaybotengine.types.updates import ChatNode, RunnerResponse, RunnerResponseObject


CHAT_EVENTS = ChatChangedEvent | NewMessageEvent
FINDER_RESULT = tuple[NewMessageEvent, list[NewMessageEvent]] | None
FINDER = Callable[[OrderEvent], FINDER_RESULT]

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
    def __init__(self, bot: Bot, config: RunnerConfig) -> None:
        self.bot = bot
        self.config = config

    async def get_runner_updates(self) -> RunnerResponse:
        chats = ChatBookmarksRequestObject(id=self.bot.userid, runner_tag=random_runner_tag())
        result = await self.bot.runner_request(requested_objects=[chats])
        return result

    async def get_sales(self, order_id: str | None = None) -> tuple[OrderPreview, ...]:
        return (await self.bot.get_sales(order_id_filter=order_id)).orders

    async def get_purchases(self, order_id: str | None = None) -> tuple[OrderPreview, ...]:
        return (await self.bot.get_purchases(order_id_filter=order_id)).orders

    async def get_nodes(self, chat_ids: list[int]) -> dict[int, RunnerResponseObject[ChatNode]]:
        nodes = {}
        objs = [NodeRequestObject(chat_id=i, runner_tag=random_runner_tag()) for i in chat_ids]

        for i in range(0, len(objs), 10):
            result = await self.bot.runner_request(requested_objects=objs[i : i + 10])

            if result.nodes is None:
                raise Exception  # todo
            nodes.update({i.data.node.id: i for i in result.nodes})

        return nodes

    async def get_chat_changed(self, runner_response: RunnerResponse) -> list[ChatChangedEvent]:
        if not runner_response.chat_bookmarks:
            return []

        result = []

        for chat_preview in reversed(runner_response.chat_bookmarks.data.chat_previews):
            cached_chat = await self.bot.storage.get_chat(chat_preview.id)

            if cached_chat == chat_preview:
                continue

            event = ChatChangedEvent(
                previous=cached_chat,
                object=chat_preview,
                tag=runner_response.chat_bookmarks.tag,
            ).as_(self.bot)

            result.append(event)

        return result

    async def get_new_message(self, events: list[ChatChangedEvent]) -> list[NewMessageEvent]:
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

    def merge_chat_events(
        self,
        chat_changed_events: list[ChatChangedEvent],
        new_message_events: list[NewMessageEvent],
    ) -> list[CHAT_EVENTS]:
        result: list[CHAT_EVENTS] = []

        chat_id_to_new_messages_mapping: dict[int, list[NewMessageEvent]] = defaultdict(list)

        for i in new_message_events:
            chat_id_to_new_messages_mapping[i.object.chat_id].append(i)

        for j in chat_changed_events:
            result.append(j)
            result.extend(chat_id_to_new_messages_mapping[j.object.id])

        return result

    async def extract_order_related_message_events(
        self,
        message_events: list[NewMessageEvent],
    ) -> OrderRelatedMessages:
        result = OrderRelatedMessages()
        for e in message_events:
            if e.object.meta.type not in _ORDER_RELATED_MESSAGE_TYPES:
                continue

            if e.object.meta.buyer_id:
                e_type = 'purchases' if e.object.meta.buyer_id == self.bot.userid else 'sales'
            elif e.object.meta.seller_id:
                e_type = 'sales' if e.object.meta.seller_id == self.bot.userid else 'purchases'
            else:
                e_type = 'unknown'

            if e_type == 'purchases' and self.config.discover_purchases:
                result.purchases.append(e)
            elif e_type == 'sales' and self.config.discover_sales:
                result.sales.append(e)
            elif e_type == 'unknown':
                result.unknown.append(e)

        return result

    async def make_order_events(self, messages: OrderRelatedMessages) -> list[OrderEvent]:
        p, s = {}, {}
        total_events: list[OrderEvent] = []

        if messages.purchases or (messages.unknown and self.config.discover_purchases):
            p = {i.id: i for i in await self.get_purchases()}

        if messages.sales or (messages.unknown and self.config.discover_sales):
            s = {i.id: i for i in await self.get_sales()}

        for e in messages.unknown:
            saved_order = await self.bot.storage.get_order(e.object.meta.order_id)
            if saved_order and saved_order.type is not OrderPreviewType.UNKNOWN:
                if (
                    saved_order.type is OrderPreviewType.PURCHASE
                    and self.config.discover_purchases
                ):
                    messages.purchases.append(e)
                    continue
                if saved_order.type is OrderPreviewType.SALE and self.config.discover_sales:
                    messages.sales.append(e)
                    continue

            if self.config.discover_purchases:
                order_preview = await self.get_purchases(order_id=e.object.meta.order_id)
                if order_preview:
                    messages.purchases.append(e)
                    p[order_preview[0].id] = order_preview[0]
                    await self.bot.storage.update_order(order_preview[0])
                    continue

            if self.config.discover_sales:
                order_preview = await self.get_sales(order_id=e.object.meta.order_id)
                if order_preview:
                    messages.sales.append(e)
                    s[order_preview[0].id] = order_preview[0]
                    await self.bot.storage.update_order(order_preview[0])
                    continue

        total_events.extend(await self._make_order_events(messages.sales, s, 'sales'))
        total_events.extend(await self._make_order_events(messages.purchases, p, 'purchases'))

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
        order_messages = await self.extract_order_related_message_events(message_events=events)
        return await self.make_order_events(order_messages)

    def merge_message_order_events(
        self,
        chat_events: list[CHAT_EVENTS | OrderEvent],
        order_events: list[OrderEvent],
    ) -> list[CHAT_EVENTS | OrderEvent]:
        chat_to_order_mapping = {i.related_new_message_event: i for i in order_events}
        result: list[CHAT_EVENTS | OrderEvent] = []

        for chat_event in chat_events:
            result.append(chat_event)
            if chat_event in chat_to_order_mapping:
                result.append(chat_to_order_mapping[chat_event])
        return result

    async def get_events(self) -> list[CHAT_EVENTS | OrderEvent]:
        runner_response = await self.get_runner_updates()

        chat_changed_events = await self.get_chat_changed(runner_response)
        new_message_events = await self.get_new_message(chat_changed_events)
        chat_events = self.merge_chat_events(chat_changed_events, new_message_events)
        order_events = await self.get_order_events(new_message_events)
        total = self.merge_message_order_events(chat_events=chat_events, order_events=order_events)

        for i in chat_changed_events:
            await self.bot.storage.update_chat(i.object)

        order_events_mapping = {}
        for j in order_events:
            if j._order_preview is None:
                continue
            order_events_mapping[j._order_preview.id] = j._order_preview

        for i in order_events_mapping.values():
            await self.bot.storage.update_order(i)

        return total
