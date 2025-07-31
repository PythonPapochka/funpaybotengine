from __future__ import annotations


__all__ = ('Runner',)


import time
import asyncio
from typing import TYPE_CHECKING, Any, Sequence
from collections.abc import AsyncGenerator

from funpaybotengine.utils import random_runner_tag
from funpaybotengine.runner.config import RunnerConfig
from funpaybotengine.types.updates import RunnerResponse
from funpaybotengine.types.requests.runner import (
    NodeRequestObject,
    ChatBookmarksRequestObject,
    OrdersCountersRequestObject,
)
from funpaybotengine.dispatching.events.base import RunnerEvent
from funpaybotengine.dispatching.events.builtin_events import NewMessageEvent, ChatChangedEvent, NewSaleEvent, SaleStatusChangedEvent, NewPurchaseEvent, PurchaseStatusChangedEvent
from funpaybotengine.types.enums import OrderStatus


if TYPE_CHECKING:
    from funpaybotengine.client.bot import Bot


class Runner:
    def __init__(self, bot: Bot):
        self._bot = bot
        self._counters_tag = random_runner_tag()
        self._config = RunnerConfig()

    @property
    def bot(self) -> Bot:
        return self._bot

    @property
    def counters_tag(self) -> str:
        return self._counters_tag

    @property
    def config(self) -> RunnerConfig:
        return self._config

    @config.setter
    def config(self, config: RunnerConfig) -> None:
        self._config = config

    async def discover_sales(self) -> None:
        result = await self.bot.get_sales()

        for i in result.orders:
            await self.bot.storage.update_order(i)

    async def discover_purchases(self) -> None:
        result = await self.bot.get_purchases()

        for i in result.orders:
            await self.bot.storage.update_order(i)

    async def discover_chats(self) -> None:
        obj = ChatBookmarksRequestObject(
            id=self.bot.userid,
            runner_tag=random_runner_tag(),
        )
        result = await self.bot.runner_request(requested_objects=[obj])

        if result.chat_bookmarks is not None:
            for i in result.chat_bookmarks.data.chat_previews:
                await self.bot.storage.update_chat(i)

    async def _get_chats_changed(self, runner_response: RunnerResponse) -> list[ChatChangedEvent]:
        if runner_response.chat_bookmarks is None:
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
            await self.bot.storage.update_chat(chat_preview)

        return result

    async def _get_new_messages(
            self,
            events: list[ChatChangedEvent]
    ) -> list[ChatChangedEvent | NewMessageEvent]:
        chat_changed_events = {e.object.id: e for e in events}
        nodes = {}

        objs = [NodeRequestObject(chat_id=i.object.id, runner_tag=random_runner_tag()) for i in events]

        for i in range(0, len(objs), 10):
            histories = await self.bot.runner_request(requested_objects=objs[i:i + 10])
            if histories.nodes is None:
                raise Exception  # todo
            nodes.update({i.data.node.id: i for i in histories.nodes})

        result: list[ChatChangedEvent | NewMessageEvent] = []
        for chat_id, event in chat_changed_events.items():
            node = nodes[chat_id]
            from_id = event.previous.last_message_id if event.previous else 0
            to_id = event.object.last_message_id

            result.append(event)
            result.extend(
                NewMessageEvent(object=message, tag=node.tag)
                for message in node.data.messages
                if from_id < message.id <= to_id
            )
        return result

    async def _make_orders(
            self,
            message_events: Sequence[ChatChangedEvent | NewMessageEvent],
            sales: bool = True,
    ) -> list[NewSaleEvent | SaleStatusChangedEvent | NewPurchaseEvent | PurchaseStatusChangedEvent]:
        new_event = NewSaleEvent if sales else NewPurchaseEvent
        changed_event = SaleStatusChangedEvent if sales else PurchaseStatusChangedEvent
        orders = await self.bot.get_sales() if sales else await self.bot.get_purchases()
        result: list[
            NewSaleEvent | NewPurchaseEvent | SaleStatusChangedEvent | PurchaseStatusChangedEvent
        ] = []

        for i in reversed(orders.orders):
            saved_order = await self.bot.storage.get_order(order_id=i.id)
            if not saved_order:
                result.append(new_event(object=i, tag=random_runner_tag()))  # todo: tag

                if i.status != OrderStatus.PAID:
                    result.append(changed_event(object=i, tag=random_runner_tag()))

                await self.bot.storage.update_order(i)
                continue

            result.append(
                changed_event(object=i, tag=random_runner_tag(), previous=saved_order)
            )
            await self.bot.storage.update_order(saved_order)
        return result


    async def _make_events(self, runner_response: RunnerResponse) -> list[RunnerEvent[Any]]:
        total_events: list[RunnerEvent[Any]] = []
        chat_changed_events = await self._get_chats_changed(runner_response)

        if self.config.discover_new_messages and chat_changed_events:
            total_events.extend(await self._get_new_messages(chat_changed_events))
        else:
            total_events.extend(i[0] for i in chat_changed_events)

        return total_events

    async def _get_runner_updates(self) -> RunnerResponse:
        counters = OrdersCountersRequestObject(
            id=self.bot.userid,
            runner_tag=self.counters_tag,
        )
        chats = ChatBookmarksRequestObject(id=self.bot.userid, runner_tag=random_runner_tag())
        result = await self.bot.runner_request(requested_objects=[counters, chats])

        if result.orders_counters:
            self._counters_tag = result.orders_counters.tag
        return result

    async def listen(
        self,
    ) -> AsyncGenerator[tuple[RunnerEvent[Any], tuple[RunnerEvent[Any], ...]]]:
        await self.discover_sales()
        await self.discover_purchases()
        await self.discover_chats()

        while True:
            start = time.time()
            try:
                result = await self._get_runner_updates()
            except Exception:
                print('err')  # todo
                continue

            events_stack = tuple(await self._make_events(result))
            for i in events_stack:
                yield i, events_stack

            time_to_sleep = self.config.interval - (time.time() - start)
            await asyncio.sleep(time_to_sleep if time_to_sleep > 0 else 0)
