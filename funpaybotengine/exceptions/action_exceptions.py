from __future__ import annotations

from .base import FunPayBotEngineError


class RefundError(FunPayBotEngineError):
    def __init__(self, order_id: str, message: str):
        self.order_id = order_id
        self.message = message

    def __str__(self) -> str:
        return self.message
