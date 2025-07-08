from __future__ import annotations

__all__ = ('BaseSession',)

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from funpaybotengine.methods.base import FunPayMethod, MethodReturnType


class BaseSession(ABC):
    @abstractmethod
    async def close(self) -> None:
        ...

    @abstractmethod
    async def make_request(self, method: FunPayMethod[MethodReturnType], timeout: float | None = None) -> MethodReturnType:
        ...

    async def __aenter__(self) -> BaseSession:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
