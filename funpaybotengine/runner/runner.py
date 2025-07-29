from __future__ import annotations


__all__ = ('Runner',)


from typing import TYPE_CHECKING, Any
from collections.abc import AsyncGenerator

from funpaybotengine.utils import random_runner_tag
from funpaybotengine.types.updates import RunnerResponse
from funpaybotengine.types.requests.runner import (
    RunnerRequestData,
    ChatBookmarksRequestObject,
    OrdersCountersRequestObject,
    NodeRequestObject,
)
from funpaybotengine.dispatching.events.base import RunnerEvent
from funpaybotengine.dispatching.events.builtin_events import ChatChangedEvent
import time
import asyncio


if TYPE_CHECKING:
    from funpaybotengine.client.bot import Bot


class Runner:
    def __init__(self, bot: Bot):
        self._bot = bot

        self._counters_tag = random_runner_tag()

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
                data = RunnerRequestData(
                    requested_objects=[obj],
                )
                result = await self.bot.runner_request(data=data)
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
        for chat in runner_response.chat_bookmarks.data.chat_previews:
            saved_chat = await self.bot.storage.get_chat(chat.id)
            if saved_chat.last_message_preview == chat.last_message_id:
                continue
            result.append(
                ChatChangedEvent(object=chat, tag=runner_response.chat_bookmarks.tag).as_(self.bot)
            )
        return result

    async def _extract_chat_histories(
            self,
            events: list[tuple[ChatChangedEvent, int]],
    ):
        events_dict = {
            event.object.id: (event, last_message_id) for event, last_message_id in events
        }

        objs = [
            NodeRequestObject(chat_id=i[0].object.id, runner_tag=random_runner_tag()) for i in events
        ]

        result = await self.bot.runner_request(requested_objects=objs)

        ...


    async def listen(
            self,
            discover_chat_histories: bool = True,
            interval: int | float = 3
    ) -> AsyncGenerator[tuple[RunnerEvent[Any], tuple[RunnerEvent[Any], ...]]]:
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

            events = tuple(await self.extract_chat_changed_updates(result))
            for i in events:
                yield i, events

            time_to_sleep = interval - (time.time() - start)
            await asyncio.sleep(time_to_sleep if time_to_sleep > 0 else 0)

    @property
    def counters_tag(self) -> str:
        return self._counters_tag
