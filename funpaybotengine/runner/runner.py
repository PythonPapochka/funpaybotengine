from __future__ import annotations


__all__ = ('Runner',)


from typing import TYPE_CHECKING

from funpaybotengine.utils import random_runner_tag


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
