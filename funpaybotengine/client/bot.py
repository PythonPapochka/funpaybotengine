from __future__ import annotations


__all__ = ('Bot',)

from typing import TYPE_CHECKING, TypeVar, ParamSpec, overload
from io import BytesIO
from collections.abc import Callable, Awaitable

from typing_extensions import Self

from funpaybotengine.types import (
    Message,
    Language,
    Subcategory,
    OrderPreview,
    RunnerResponse,
    OrderPreviewsBatch,
)
from funpaybotengine.methods import (
    GetSales,
    GetChatPage,
    GetMainPage,
    UploadImage,
    FunPayMethod,
    GetOrderPage,
    GetPurchases,
    RunnerRequest,
    GetChatHistory,
    GetProfilePage,
    MethodReturnType,
    GetSubcategoryPage,
)
from funpaybotengine.types.enums import OrderStatus, SubcategoryType
from funpaybotengine.types.pages import (
    ChatPage,
    MainPage,
    OrderPage,
    ProfilePage,
    SubcategoryPage,
)
from funpaybotengine.types.requests import RunnerRequestData
from funpaybotengine.client.base_bot import BaseBot
from funpaybotengine.client.session.base import Response
from funpaybotengine.client.categories_cache import CategoriesCache
from funpaybotengine.client.session.aiohttp_session import AioHttpSession


if TYPE_CHECKING:
    from funpaybotengine.client.session.base import BaseSession


P = ParamSpec('P')
R = TypeVar('R')


def need_preinitialization(
    func: Callable[P, Awaitable[R]],
) -> Callable[P, Awaitable[R]]:
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        if not args or not isinstance(args[0], Bot):
            raise RuntimeError('Can be used only with Bot methods.')  # todo

        self: Bot = args[0]
        if not self.initialized:
            await self.update()
        return await func(*args, **kwargs)

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

    async def get_sales(
        self,
        from_order_id: str | None = None,
        order_id_filter: str | None = None,
        buyer_username_filter: str | None = None,
        status_filter: OrderStatus | str | None = None,
        game_id_filter: str | None = None,
        other_filters: dict[str, str] | None = None,
    ) -> OrderPreviewsBatch:
        m = GetSales(
            from_order_id=from_order_id,
            order_id_filter=order_id_filter,
            buyer_username_filter=buyer_username_filter,
            status_filter=status_filter,
            game_id_filter=game_id_filter,
            other_filters=other_filters,
        )

        result = await self.make_request(m)
        return result.response_obj

    async def get_purchases(
        self,
        from_order_id: str | None = None,
        order_id_filter: str | None = None,
        seller_username_filter: str | None = None,
        status_filter: OrderStatus | str | None = None,
        game_id_filter: str | None = None,
        other_filters: dict[str, str] | None = None,
    ) -> OrderPreviewsBatch:
        m = GetPurchases(
            from_order_id=from_order_id,
            order_id_filter=order_id_filter,
            seller_username_filter=seller_username_filter,
            status_filter=status_filter,
            game_id_filter=game_id_filter,
            other_filters=other_filters,
        )

        result = await self.make_request(m)
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

    @overload
    async def get_subcategory_page(
        self,
        subcategory_type: SubcategoryType = ...,
        subcategory_id: int = ...,
        subcategory: None = ...,
    ) -> SubcategoryPage: ...

    @overload
    async def get_subcategory_page(
        self,
        subcategory_type: None = ...,
        subcategory_id: None = ...,
        subcategory: Subcategory = ...,
    ) -> SubcategoryPage: ...

    async def get_subcategory_page(
        self,
        subcategory_type: SubcategoryType | None = None,
        subcategory_id: int | None = None,
        subcategory: Subcategory | None = None,
    ) -> SubcategoryPage:
        assert (
            isinstance(subcategory_type, SubcategoryType)
            and isinstance(subcategory_id, int)
        ) or isinstance(subcategory, Subcategory), (
            f'Invalid subcategory input: '
            f"either provide both 'subcategory_type' and 'subcategory_id' "
            f"(got {subcategory_type=}, {subcategory_id=}), or provide 'subcategory' object "
            f'(got {subcategory=}).'
        )

        if subcategory is not None:
            t, i = subcategory.type, subcategory.id
        else:
            t, i = subcategory_type, subcategory_id  # type: ignore[assignment]  # asserted above

        result = await self.make_request(GetSubcategoryPage(type=t, id=i))
        return result.response_obj

    @overload
    async def get_order_page(
        self, order_id: str = ..., order: None = ...
    ) -> OrderPage: ...

    @overload
    async def get_order_page(
        self, order_id: None = ..., order: OrderPreview | OrderPage = ...
    ) -> OrderPage: ...

    async def get_order_page(
        self, order_id: str | None = None, order: OrderPreview | OrderPage | None = None
    ) -> OrderPage:
        assert isinstance(order_id, str) or isinstance(
            order, OrderPreview | OrderPage
        ), (
            f'Invalid order_id input: '
            f"either provide 'order_id' (got {order_id=}), "
            f"or provide 'order' object (got {order=})."
        )

        if order_id:
            i = order_id
        else:
            i = order.id if isinstance(order, OrderPreview) else order.order_id  # type: ignore[union-attr]
            # asserted above

        result = await self.make_request(GetOrderPage(id=i))
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

        return self
