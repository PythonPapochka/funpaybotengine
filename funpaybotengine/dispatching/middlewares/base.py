from __future__ import annotations

__all__ = ('Middleware', )


from abc import ABC, abstractmethod
from typing import Any


class Middleware(ABC):

    @abstractmethod
    async def __call__(self, *args, **kwargs) -> Any: ...
