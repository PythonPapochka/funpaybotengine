from __future__ import annotations


__all__ = ('Bot',)

from typing import TYPE_CHECKING
from io import BytesIO

from funpaybotengine.methods.base import FunPayMethod, MethodReturnType
from funpaybotengine.client.base_bot import BaseBot
from funpaybotengine.methods.upload_image import UploadImage
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
        self._locale = ''

    @property
    def golden_key(self) -> str:
        return self._golden_key

    @property
    def session(self) -> BaseSession:
        return self._session

    async def upload_chat_image(self, file: str | BytesIO) -> int:
        return await self.make_request(UploadImage(file=file))

    async def get_chat_history(
        self, chat_id: int | str, last_message_id: int = 999999999999
    ):
        return await self.make_request(
            GetChatHistory(chat_id=chat_id, before_message_id=last_message_id)
        )

    async def get_main_page(self):
        return await self.make_request(GetMainPage())

    async def get_chat_page(self, chat_id: int | str):
        return await self.make_request(GetChatPage(chat_id=chat_id))

    async def make_request(
        self, method: FunPayMethod[MethodReturnType]
    ) -> MethodReturnType:
        return await self.session.make_request(method.as_(self))

    @property
    def locale(self) -> str:
        return self._locale
