from __future__ import annotations

from abc import ABC, abstractmethod


class BaseBot(ABC):
    @property
    @abstractmethod
    def golden_key(self) -> str: ...

    @property
    @abstractmethod
    def locale(self) -> str: ...
