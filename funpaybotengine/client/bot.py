from __future__ import annotations


__all__ = ('Bot',)

from typing import TYPE_CHECKING
from io import BytesIO

from typing_extensions import Self

from funpaybotengine.types import Message, Language, RunnerResponse
from funpaybotengine.methods import (
    GetChatPage,
    GetMainPage,
    FunPayMethod,
    RunnerRequest,
    GetChatHistory,
    GetProfilePage,
    MethodReturnType,
    UploadImage,
)
from funpaybotengine.types.pages import ChatPage, MainPage, ProfilePage
from funpaybotengine.types.requests import RunnerRequestData
from funpaybotengine.client.base_bot import BaseBot
from funpaybotengine.client.session.base import Response
from funpaybotengine.client.categories_cache import CategoriesCache
from funpaybotengine.client.session.aiohttp_session import AioHttpSession
from typing import ParamSpec, Concatenate, TypeVar, Any
from collections.abc import Callable, Awaitable, Coroutine


if TYPE_CHECKING:
    from funpaybotengine.client.session.base import BaseSession


P = ParamSpec('P')
R = TypeVar('R')


def need_preinitialization(
        func: Callable[Concatenate['Bot', P], Awaitable[R]]
) -> Callable[Concatenate[P], Coroutine[Any, Any, R]]:
    async def wrapper(self: 'Bot', /, *args: P.args, **kwargs: P.kwargs) -> R:
        if not self.initialized:
            await self.update()
        return await func(self, *args, **kwargs)
    return wrapper


class Bot(BaseBot):
    def __init__(self, golden_key: str, session: BaseSession | None = None):
        self._golden_key = golden_key
        self._csrf_token: str | None = None
        self._phpsessid: str | None = None
        self._session = session or AioHttpSession(proxy=None)
        self._locale: Language = Language.RU

        self._userid: int | None = None
        self._username: str | None = None
        self._categories_cache: CategoriesCache | None = None

    @property
    def anonymous(self) -> bool:
        """Whether this bot instance is anonymous or not."""
        return not bool(self._golden_key)

    @property
    def initialized(self) -> bool:
        """
        Whether this bot instance is initialized or not.

        To initialize the bot instance, use ``Bot.update`` method.
        """
        return bool(self._csrf_token) and bool(self._phpsessid)

    @property
    def golden_key(self) -> str:
        """
        Golden key (token).
        """
        return self._golden_key

    @property
    def csrf_token(self) -> str | None:
        """
        CSRF token. Available only after initialization (``Bot.update`` method).
        """
        return self._csrf_token

    @csrf_token.setter
    def csrf_token(self, value: str | None) -> None:
        self._csrf_token = value

    @property
    def phpsessid(self) -> str | None:
        """
        PHPSESSID. Available only after initialization (``Bot.update`` method).
        """
        return self._phpsessid

    @phpsessid.setter
    def phpsessid(self, value: str | None) -> None:
        self._phpsessid = value

    @property
    def session(self) -> BaseSession:
        """
        Bot session.
        """
        return self._session

    @property
    def locale(self) -> Language:
        """
        Bot locale. Available only after initialization (``Bot.update`` method).
        """
        return self._locale

    @locale.setter
    def locale(self, value: Language) -> None:
        self._locale = value

    @property
    def categories_cache(self) -> CategoriesCache | None:
        return self._categories_cache

    @need_preinitialization
    async def runner_request(self, data: RunnerRequestData) -> RunnerResponse:
        """
        Makes request to the runner.

        :param data: runner data.

        :return: Runner response.
        """
        data.csrf_token = self.csrf_token
        result = await self.make_request(RunnerRequest(request=data))
        return result.response_obj

    async def upload_chat_image(self, file: str | BytesIO) -> int:
        """
        Uploads an image to FunPay servers for use in chat messages.

        The image can later be referenced in chat via its assigned image ID.

        :param file: Path to the image file (as a string) or an in-memory
        file-like object (``BytesIO``).

        :return: Unique FunPay image ID assigned to the uploaded image.
        """
        result = await self.make_request(UploadImage(file=file))
        return result.response_obj

    async def get_chat_history(
        self, chat_id: int | str, before_message_id: int = 999999999999
    ) -> list[Message]:
        """
        Retrieves the 50 most recent messages in a chat,
        sent before the specified message ID.

        Also marks the chat as read.

        :param chat_id: Chat ID or name.
        :param before_message_id:
            Message ID to paginate from —
            only messages sent **before** this ID will be returned.
            Defaults to a large number (``999999999999``)
            to fetch the most recent messages.

        :return: A list of up to 50 ``Message`` objects, sorted from oldest to newest.
        """
        result = await self.make_request(
            GetChatHistory(chat_id=chat_id, before_message_id=before_message_id)
        )
        return result.response_obj

    async def get_main_page(self) -> MainPage:
        """
        Retrieves the FunPay main page.
        """
        result = await self.make_request(GetMainPage())
        return result.response_obj

    async def get_chat_page(self, chat_id: int | str) -> ChatPage:
        """
        Retrieves the chat page.

        :param chat_id: Chat ID or name.
        """
        result = await self.make_request(GetChatPage(chat_id=chat_id))
        return result.response_obj

    async def get_profile_page(self, id: int) -> ProfilePage:
        result = await self.make_request(GetProfilePage(id=id))
        return result.response_obj

    async def make_request(
        self, method: FunPayMethod[MethodReturnType]
    ) -> Response[MethodReturnType]:
        if not self.initialized:
            await self.update()
        return await self.session.make_request(method.as_(self))

    async def update(self, change_locale: Language | None = None) -> Self:
        result = await self.session.make_request(
            GetMainPage(change_locale=change_locale).as_(self)
        )

        self.csrf_token = result.response_obj.app_data.csrf_token
        self.locale = result.response_obj.app_data.locale
        self.phpsessid = result.response_cookies.get('PHPSESSID')
        self._userid = result.response_obj.header.user_id
        self._username = result.response_obj.header.username
        self._categories_cache = CategoriesCache(result.response_obj.categories)

        print(f'CSRF token: {self.csrf_token}')
        print(f'PHPSESSID: {self.phpsessid}')

        return self
