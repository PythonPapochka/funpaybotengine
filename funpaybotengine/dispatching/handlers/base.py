__all__ = ('Handler', )

from abc import ABC, abstractmethod
from typing import Any


class Handler(ABC):
    @abstractmethod
    async def __call__(self, *args: Any, **kwargs: Any) -> Any: ...
