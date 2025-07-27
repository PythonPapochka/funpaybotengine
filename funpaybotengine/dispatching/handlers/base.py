from abc import abstractmethod, ABC


__all__ = ('Handler', )

from typing import Any


class Handler(ABC):
    @abstractmethod
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...