from .base import FunPayBotEngineError
from typing import Any


class BotIsNotBoundError(FunPayBotEngineError):
    def __init__(self, obj: Any) -> None:
        self.obj = obj
        super().__init__(
            f'Instance of {obj.__class__.__name__} is not bound to any Bot instance.'
        )
