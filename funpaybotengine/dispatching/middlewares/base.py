from abc import abstractmethod, ABC


__all__ = ('Middleware', )

from typing import Any


class Middleware(ABC):
    @abstractmethod
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...