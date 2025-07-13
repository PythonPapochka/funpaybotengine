from __future__ import annotations

from abc import ABC, abstractmethod


class BaseBot(ABC):
    @property
    @abstractmethod
    def golden_key(self) -> str: ...

    @property
    @abstractmethod
    def locale(self) -> str: ...

    @property
    @abstractmethod
    def csrf_token(self) -> str | None: ...

    @csrf_token.setter
    @abstractmethod
    def csrf_token(self, value: str) -> None: ...

    @property
    @abstractmethod
    def phpsessid(self) -> str | None: ...

    @phpsessid.setter
    @abstractmethod
    def phpsessid(self, value: str) -> None: ...