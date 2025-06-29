from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from funpaybotengine.client.bot import Bot


class BindableObject:
    def __init__(self, bot: Bot | None) -> None:
        self._bot = bot

    def as_(self, bot) -> 'BindableObject':
        if not isinstance(self._bot, Bot):
            raise Exception('Not a bot instance')  # todo: exceptions

        self._bot = bot
        return self

    @property
    def bot(self) -> Bot | None:
        return self._bot
