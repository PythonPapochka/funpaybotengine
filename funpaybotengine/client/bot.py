from __future__ import annotations

__all__ = ('Bot', )

from typing import TYPE_CHECKING
from funpaybotengine.client.session.aiohttp_session import AioHttpSession

if TYPE_CHECKING:
    from funpaybotengine.client.session.base import BaseSession



class Bot:
    def __init__(self,
                 golden_key: str,
                 session: BaseSession | None = None):
        self._golden_key = golden_key
        self._session = session or AioHttpSession(golden_key=golden_key, proxy=None)

    @property
    def golden_key(self) -> str:
        return self._golden_key

    @property
    def session(self) -> BaseSession:
        return self.session
