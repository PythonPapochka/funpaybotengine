from __future__ import annotations


__all__ = ('Bot',)

from typing import TYPE_CHECKING

from funpaybotengine.methods.base import FunPayMethod, MethodReturnType
from funpaybotengine.client.base_bot import BaseBot
from funpaybotengine.methods.get_chat_page import GetChatPage
from funpaybotengine.methods.get_main_page import GetMainPage
from funpaybotengine.methods.get_chat_history import GetChatHistory
from funpaybotengine.client.session.aiohttp_session import AioHttpSession


if TYPE_CHECKING:
    from funpaybotengine.client.session.base import BaseSession


class Bot(BaseBot):
    def __init__(self, golden_key: str, session: BaseSession | None = None):
        self._golden_key = golden_key
        self._session = session or AioHttpSession(proxy=None)

    @property
    def golden_key(self) -> str:
        return self._golden_key

    @property
    def session(self) -> BaseSession:
        return self._session

    async def get_chat_history(
        self, chat_id: int | str, last_message_id: int = 999999999999
    ):
        method = GetChatHistory(chat_id=chat_id, before_message_id=last_message_id).as_(
            self
        )
        return await self.session.make_request(method)

    async def get_main_page(self):
        method = GetMainPage().as_(self)
        return await self.session.make_request(method)

    async def get_chat_page(self, chat_id: int | str):
        method = GetChatPage(chat_id=chat_id).as_(self)
        return await self.session.make_request(method)

    async def make_request(
        self, method: FunPayMethod[MethodReturnType]
    ) -> MethodReturnType:
        return await self.session.make_request(method.as_(self))
