from __future__ import annotations


__all__ = ('Bot',)

from typing import TYPE_CHECKING
from io import BytesIO

from funpaybotengine.types import Message
from funpaybotengine.methods import (
    GetChatPage,
    GetMainPage,
    UploadImage,
    FunPayMethod,
    GetChatHistory,
    MethodReturnType,
)
from funpaybotengine.types.pages import ChatPage, MainPage
from funpaybotengine.client.base_bot import BaseBot
from funpaybotengine.client.session.aiohttp_session import AioHttpSession


if TYPE_CHECKING:
    from funpaybotengine.client.session.base import BaseSession


class Bot(BaseBot):
    def __init__(self, golden_key: str, session: BaseSession | None = None):
        self._golden_key = golden_key
        self._csrf_token: str | None = None
        self._phpsessid: str | None = None
        self._session = session or AioHttpSession(proxy=None)
        self._locale = ''

    @property
    def golden_key(self) -> str:
        return self._golden_key

    @property
    def csrf_token(self) -> str | None:
        return self._csrf_token

    @csrf_token.setter
    def csrf_token(self, value: str | None) -> None:
        self._csrf_token = value

    @property
    def phpsessid(self) -> str | None:
        return self._phpsessid

    @phpsessid.setter
    def phpsessid(self, value: str | None) -> None:
        self._phpsessid = value

    @property
    def session(self) -> BaseSession:
        return self._session

    @property
    def locale(self) -> str:
        return self._locale

    async def upload_chat_image(self, file: str | BytesIO) -> int:
        return await self.make_request(UploadImage(file=file))

    async def get_chat_history(
        self, chat_id: int | str, last_message_id: int = 999999999999
    ) -> list[Message]:
        return await self.make_request(
            GetChatHistory(chat_id=chat_id, before_message_id=last_message_id)
        )

    async def get_main_page(self) -> MainPage:
        return await self.make_request(GetMainPage())

    async def get_chat_page(self, chat_id: int | str) -> ChatPage:
        return await self.make_request(GetChatPage(chat_id=chat_id))

    async def make_request(
        self, method: FunPayMethod[MethodReturnType]
    ) -> MethodReturnType:
        return await self.session.make_request(method.as_(self))
