from __future__ import annotations

from typing import TYPE_CHECKING
from collections import defaultdict
from collections.abc import Callable

from funpaybotengine.utils import random_runner_tag
from funpaybotengine.loggers import runner_logger
from funpaybotengine.types.enums import OrderStatus
from funpaybotengine.types.enums import MessageType
from dataclasses import dataclass, field
from funpaybotengine.runner.config import RunnerConfig
from funpaybotengine.dispatching.events import (
    NewSaleEvent,
    NewMessageEvent,
    ChatChangedEvent,
    NewPurchaseEvent,
    SaleStatusChangedEvent,
    PurchaseStatusChangedEvent,
)
from funpaybotengine.types.requests.runner import (
    NodeRequestObject,
    ChatBookmarksRequestObject,
    OrdersCountersRequestObject,
)


if TYPE_CHECKING:
    from funpaybotengine.client.bot import Bot
    from funpaybotengine.types.updates import ChatNode, RunnerResponse, RunnerResponseObject


CHAT_EVENTS = ChatChangedEvent | NewMessageEvent

ORDER_EVENTS = (
    NewSaleEvent | SaleStatusChangedEvent | NewPurchaseEvent | PurchaseStatusChangedEvent
)

FINDER_RESULT = tuple[NewMessageEvent, list[NewMessageEvent]] | None

FINDER = Callable[[ORDER_EVENTS], FINDER_RESULT]

_ORDER_RELATED_MESSAGE_TYPES = [
    MessageType.NEW_ORDER,
    MessageType.ORDER_CLOSED,
    MessageType.ORDER_CLOSED_BY_ADMIN,
    MessageType.ORDER_REFUNDED,
    MessageType.ORDER_PARTIALLY_REFUNDED,
    MessageType.ORDER_REOPENED,
]

@dataclass
class OrderRelatedMessages:
    sales: list[NewMessageEvent] = field(default_factory=list)
    purchases: list[NewMessageEvent] = field(default_factory=list)
    unknown: list[NewMessageEvent] = field(default_factory=list)


class EventCollector:
    def __init__(self, bot: Bot, config: RunnerConfig) -> None:
        self.bot = bot
        self.counters_tag = random_runner_tag()
        self.config = config

    async def _get_runner_updates(self) -> RunnerResponse:
        counters = OrdersCountersRequestObject(
            id=self.bot.userid,
            runner_tag=self.counters_tag,
        )
        chats = ChatBookmarksRequestObject(id=self.bot.userid, runner_tag=random_runner_tag())
        result = await self.bot.runner_request(requested_objects=[counters, chats])

        if result.orders_counters:
            self.counters_tag = result.orders_counters.tag
        return result

    async def _extract_chat_changed_events(
        self, runner_response: RunnerResponse
    ) -> list[ChatChangedEvent]:
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

    async def _get_nodes(self, chat_ids: list[int]) -> dict[int, RunnerResponseObject[ChatNode]]:
        nodes = {}

        objs = [NodeRequestObject(chat_id=i, runner_tag=random_runner_tag()) for i in chat_ids]

        for i in range(0, len(objs), 10):
            result = await self.bot.runner_request(requested_objects=objs[i : i + 10])

            if result.nodes is None:
                raise Exception  # todo

            nodes.update({i.data.node.id: i for i in result.nodes})

        return nodes

    async def _get_new_message_events(
        self,
        events: list[ChatChangedEvent],
    ) -> list[NewMessageEvent]:
        chat_changed_events = {e.object.id: e for e in events}

        nodes = await self._get_nodes([e.object.id for e in events])

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

    async def _merge_chat_events(
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

    async def _extract_order_related_message_events(
            self,
            message_events: list[NewMessageEvent],
    ) -> OrderRelatedMessages:
        result = OrderRelatedMessages()
        for e in message_events:
            if e.object.meta.type not in _ORDER_RELATED_MESSAGE_TYPES:
                continue

            if e.object.meta.buyer_id:
                if e.object.meta.buyer_id == self.bot.userid:
                    result.purchases.append(e)
                else:
                    result.sales.append(e)
            elif e.object.meta.seller_id:
                if e.object.meta.seller_id == self.bot.userid:
                    result.sales.append(e)
                else:
                    result.purchases.append(e)
            else:
                result.unknown.append(e)

        return result

    async def get_events(self) -> list[CHAT_EVENTS | ORDER_EVENTS]:
        runner_response = await self._get_runner_updates()

        chat_changed_events = await self._extract_chat_changed_events(runner_response)
        new_message_events = await self._get_new_message_events(chat_changed_events)
        chat_events = await self._merge_chat_events(chat_changed_events, new_message_events)

        return [*chat_events]
