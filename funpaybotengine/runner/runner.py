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
)
from funpaybotengine.dispatching.events.base import RunnerEvent
from funpaybotengine.dispatching.events.builtin_events import ChatChangedEvent
import asyncio


if TYPE_CHECKING:
    from funpaybotengine.client.bot import Bot


class Runner:
    def __init__(self, bot: Bot):
        self._bot = bot

        self._messages_tag = random_runner_tag()
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
            await self.bot.storage.set_order_status(i.id, i.status)

    async def discover_purchases(self) -> None:
        while True:
            try:
                result = await self.bot.get_purchases()
                break
            except:
                continue

        for i in result.orders:
            await self.bot.storage.set_order_status(i.id, i.status)

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
                await self.bot.storage.set_last_message_id(i.id, i.last_message_id)

            self._messages_tag = result.chat_bookmarks.tag

    async def extract_chat_changed_updates(
        self, runner_response: RunnerResponse
    ) -> list[ChatChangedEvent]:
        if runner_response.chat_bookmarks is None:
            return []

        result = []
        for i in runner_response.chat_bookmarks.data.chat_previews:
            last_message_id = await self.bot.storage.get_last_message_id(i.id)
            if last_message_id != i.last_message_id:
                result.append(ChatChangedEvent(object=i, tag=self._messages_tag).as_(self.bot))

        self._messages_tag = runner_response.chat_bookmarks.tag
        return result

    async def listen(self) -> AsyncGenerator[RunnerEvent[Any]]:
        await self.discover_sales()
        await self.discover_purchases()
        await self.discover_chats()

        while True:
            counters = OrdersCountersRequestObject(
                id=self.bot._userid, runner_tag=self.counters_tag
            )
            chats = ChatBookmarksRequestObject(id=self.bot._userid, runner_tag=self._messages_tag)
            data = RunnerRequestData(
                requested_objects=[counters, chats],
            )
            try:
                result = await self.bot.runner_request(data=data)
            except Exception:
                print('err')  # todo
                continue

            events = await self.extract_chat_changed_updates(result)
            for i in events:
                yield i

            await asyncio.sleep(3)

    @property
    def messages_tag(self) -> str:
        return self._messages_tag

    @property
    def counters_tag(self) -> str:
        return self._counters_tag
