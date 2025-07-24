from __future__ import annotations


__all__ = ('Handler',)

from typing import Any
from abc import ABC, abstractmethod


class Handler(ABC):
    @abstractmethod
    async def __call__(self, *args: Any, **kwargs: Any) -> Any: ...
