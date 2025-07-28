from __future__ import annotations


__all__ = ('Runner',)


from typing import TYPE_CHECKING

from funpaybotengine.utils import random_runner_tag


if TYPE_CHECKING:
    from funpaybotengine.client.base_bot import BaseBot


class Runner(BaseBot):
    def __init__(self, bot: BaseBot):
        self._bot = bot

        self._messages_tag = random_runner_tag()
        self._counters_tag = random_runner_tag()

    @property
    def bot(self) -> BaseBot:
        return self._bot
