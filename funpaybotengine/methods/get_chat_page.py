from __future__ import annotations


__all__ = ('GetChatPage',)

from typing import TYPE_CHECKING

from pydantic import BaseModel
from funpayparsers.parsers.page_parsers import ChatPageParser

from funpaybotengine.types.enums import Language
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.types.pages.chat_page import ChatPage


if TYPE_CHECKING:
    from funpayparsers.types.pages import ChatPage as ParserChatPage


class GetChatPage(FunPayMethod[ChatPage], BaseModel):
    """
    Get chat method (``https://funpay.com/chat/history``).

    Returns max. 50 messages before ``before_message_id``.
    """

    chat_id: int | str
    """Chat ID."""

    def __init__(self, chat_id: int | str, locale: Language | None = None):
        """
        :param chat_id: Chat ID.
        :param locale: FunPay locale.
            If specified and ``ignore_locale`` is ``False``,
            it will override bots locale when making a request.
            Defaults to ``None``.
        """
        super().__init__(
            url='chat/',
            locale=locale,
            data={'node': str(chat_id)},
            parser_cls=ChatPageParser,
            allow_anonymous=True,
            chat_id=chat_id,
        )

    def transform_result(self, chat_page: ParserChatPage) -> ChatPage:
        return ChatPage.model_validate(chat_page, context={'bot': self._bot})
