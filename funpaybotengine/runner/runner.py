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

    @property
    def bot(self) -> Bot:
        return self._bot

    async def discover_chats(self) -> None:
        obj = ChatBookmarksRequestObject(
            id=self.bot.userid,
            runner_tag=random_runner_tag(),
        )
        result = await self.bot.runner_request(requested_objects=[obj])

        if result.chat_bookmarks is not None:
            for i in result.chat_bookmarks.data.chat_previews:
                await self.bot.session_storage.update_chat(i)

    async def listen(
        self,
        config: RunnerConfig | None = None
    ) -> AsyncGenerator[tuple[RunnerEvent[Any], tuple[RunnerEvent[Any], ...]]]:
        await self.discover_chats()

        config = config or RunnerConfig()
        collector = EventCollector(self.bot, config)

        while True:
            start = time.time()
            try:
                result = await collector.get_events()
            except Exception:
                import traceback
                print(traceback.format_exc())  # todo: yield exception event
                continue

            events_stack = tuple(result)
            for i in events_stack:
                yield i, events_stack

            time_to_sleep = config.interval - (time.time() - start)
            if time_to_sleep > 0:
                await asyncio.sleep(time_to_sleep)
