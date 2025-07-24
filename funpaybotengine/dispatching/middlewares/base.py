from __future__ import annotations


__all__ = ('Middleware',)


from typing import Any
from abc import ABC, abstractmethod


class Middleware(ABC):
    @abstractmethod
    async def __call__(self, *args: Any, **kwargs: Any) -> Any: ...
