from __future__ import annotations

__all__ = (
    'BotNotBoundError',
    'BotNotInitializedError'
)

from .base import FunPayBotEngineError
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from funpaybotengine.client.bot import Bot


class BotNotBoundError(FunPayBotEngineError, RuntimeError):
    def __init__(self, obj: Any) -> None:
        self.obj = obj
        super().__init__(
            f'Instance of {obj.__class__.__name__} is not bound to any Bot instance.'
        )


class BotNotInitializedError(FunPayBotEngineError, RuntimeError):
    def __init__(self, bot: Bot) -> None:
        super().__init__(
            f'Bot instance {bot} is not initialized.\n'
            f'Use `await bot.update()` to initialize it.'
        )
