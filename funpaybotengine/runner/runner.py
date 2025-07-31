from __future__ import annotations


__all__ = ('Runner',)


from typing import TYPE_CHECKING, Any
from collections.abc import AsyncGenerator

from funpaybotengine.utils import random_runner_tag
from funpaybotengine.types.updates import RunnerResponse
from funpaybotengine.types.requests.runner import (
    ChatBookmarksRequestObject,
    OrdersCountersRequestObject,
    NodeRequestObject,
)
from funpaybotengine.dispatching.events.base import RunnerEvent
from funpaybotengine.dispatching.events.builtin_events import ChatChangedEvent, NewMessageEvent
from funpaybotengine.runner.config import RunnerConfig
import time
import asyncio


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

    async def discover_sales(self) -> None:
        while True:
            try:
                result = await self.bot.get_sales()
                break
            except:
                continue

        for i in result.orders:
            await self.bot.storage.update_order(i)

    async def discover_purchases(self) -> None:
        while True:
            try:
                result = await self.bot.get_purchases()
                break
            except:
                continue

        for i in result.orders:
            await self.bot.storage.update_order(i)

    async def discover_chats(self) -> None:
        while True:
            try:
                obj = ChatBookmarksRequestObject(
                    id=self.bot._userid, runner_tag=random_runner_tag()
                )
                result = await self.bot.runner_request(requested_objects=[obj])
                break
            except:
                continue

        if result.chat_bookmarks is not None:
            for i in result.chat_bookmarks.data.chat_previews:
                await self.bot.storage.update_chat(i)

    async def extract_chat_changed_updates(
            self,
            runner_response: RunnerResponse
    ) -> list[ChatChangedEvent]:
        if runner_response.chat_bookmarks is None:
            return []

        result = []
        for chat_preview in runner_response.chat_bookmarks.data.chat_previews:
            cached_chat = await self.bot.storage.get_chat(chat_preview.id)
            if cached_chat == chat_preview:
                continue

            event = ChatChangedEvent(
                previous=cached_chat,
                object=chat_preview,
                tag=runner_response.chat_bookmarks.tag
            ).as_(self.bot)

            result.append(event)
            await self.bot.storage.update_chat(chat_preview)

        return result

    async def _extract_chat_histories(
            self,
            events: list[ChatChangedEvent],
    ) -> list[ChatChangedEvent | NewMessageEvent]:
        events_dict = {
            event.object.id: event for event in events
        }
        result: list[ChatChangedEvent | NewMessageEvent] = []

        objs = [
            NodeRequestObject(chat_id=i.object.id, runner_tag=random_runner_tag()) for i in events
        ]
        histories = await self.bot.runner_request(requested_objects=objs)

        if not histories.nodes:
            raise Exception  # todo

        for node in histories.nodes:
            chat_changed_event = events_dict[node.data.node.id]
            from_id = chat_changed_event.previous.last_message_id if chat_changed_event.previous else 0
            to_id = chat_changed_event.object.last_message_id
            result.append(chat_changed_event)
            result.extend(
                NewMessageEvent(object=message, tag=node.tag)
                for message in node.data.messages if from_id < message.id <= to_id
            )
        return result

    async def listen(self) -> AsyncGenerator[tuple[RunnerEvent[Any], tuple[RunnerEvent[Any], ...]]]:
        await self.discover_sales()
        await self.discover_purchases()
        await self.discover_chats()

        while True:
            start = time.time()
            counters = OrdersCountersRequestObject(
                id=self.bot._userid, runner_tag=self.counters_tag
            )
            chats = ChatBookmarksRequestObject(id=self.bot._userid, runner_tag=random_runner_tag())
            try:
                result = await self.bot.runner_request(
                    requested_objects=[counters,chats]
                )
            except Exception:
                print('err')  # todo
                continue

            chat_changed_events = await self.extract_chat_changed_updates(result)
            if self.config.discover_new_messages and chat_changed_events:
                total_events = await self._extract_chat_histories(chat_changed_events)
            else:
                total_events = [i[0] for i in chat_changed_events]
            # todo: order events

            events_stack = tuple(total_events)
            for i in total_events:
                yield i, events_stack

            time_to_sleep = self.config.interval - (time.time() - start)
            await asyncio.sleep(time_to_sleep if time_to_sleep > 0 else 0)

    @property
    def counters_tag(self) -> str:
        return self._counters_tag

    @property
    def config(self) -> RunnerConfig:
        return self._config

    @config.setter
    def config(self, config: RunnerConfig) -> None:
        self._config = config