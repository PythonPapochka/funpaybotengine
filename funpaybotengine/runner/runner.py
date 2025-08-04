from __future__ import annotations


__all__ = ('Runner',)


import time
import asyncio
from typing import TYPE_CHECKING, Any
from collections.abc import AsyncGenerator

from funpaybotengine.utils import random_runner_tag
from funpaybotengine.runner.config import RunnerConfig
from funpaybotengine.types.requests.runner import ChatBookmarksRequestObject
from funpaybotengine.runner.event_collector import EventCollector
from funpaybotengine.dispatching.events.base import RunnerEvent


if TYPE_CHECKING:
    from funpaybotengine.client.bot import Bot


class Runner:
    def __init__(self, bot: Bot):
        self._bot = bot
        self._counters_tag = random_runner_tag()
        self._config = RunnerConfig()
        self._collector = EventCollector(bot=self.bot, config=self._config)

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

    async def listen(
        self,
    ) -> AsyncGenerator[tuple[RunnerEvent[Any], tuple[RunnerEvent[Any], ...]]]:
        await self.discover_sales()
        await self.discover_purchases()
        await self.discover_chats()

        while True:
            start = time.time()
            try:
                result = await self._collector.get_events()
            except Exception:
                print('err')  # todo
                import traceback

                print(traceback.format_exc())
                continue

            events_stack = tuple(result)
            for i in events_stack:
                yield i, events_stack

            time_to_sleep = self.config.interval - (time.time() - start)
            await asyncio.sleep(time_to_sleep if time_to_sleep > 0 else 0)
