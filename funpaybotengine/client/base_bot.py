from __future__ import annotations

from typing import TYPE_CHECKING
from abc import ABC, abstractmethod


if TYPE_CHECKING:
    from funpaybotengine.types.enums import Language
    from funpaybotengine.methods.base import FunPayMethod, MethodReturnType
    from funpaybotengine.client.session.base import Response


class BaseBot(ABC):
    @property
    @abstractmethod
    def golden_key(self) -> str: ...

    @property
    @abstractmethod
    def locale(self) -> Language: ...

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

    @property
    @abstractmethod
    def anonymous(self) -> bool: ...

    async def make_request(
        self, method: FunPayMethod[MethodReturnType]
    ) -> Response[MethodReturnType]: ...
