from __future__ import annotations


__all__ = ('GetChatHistory',)

import json
from typing import TYPE_CHECKING

from pydantic import BaseModel
from funpayparsers.parsers import MessagesParser

from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.types.messages import Message


if TYPE_CHECKING:
    from funpayparsers.types import Message as ParserMessage


class GetChatHistory(FunPayMethod[list[Message]], BaseModel):
    """
    Get chat history method (``https://funpay.com/chat/history``).

    Returns max. 50 messages before ``before_message_id``.
    """

    chat_id: int | str
    """Chat ID."""

    before_message_id: int = 99999999999
    """
    Message ID to paginate history **backwards from** (exclusive).

    Messages with IDs **less than** this one will be returned,
    i.e. history will be fetched in reverse order *before* this message.
    
    Defaults to ``99999999999``
    """

    locale: str = ''
    """
    FunPay locale (``'en'`` / ``'uk'``).

    Defaults to ``''`` (Russian).
    """

    def __init__(
        self, chat_id: int | str, before_message_id: int = 99999999999, locale: str = ''
    ):
        """
        :param chat_id: Chat ID.
        :param before_message_id: Message ID to paginate history **backwards from**
            (exclusive).
            Messages with IDs **less than** this one will be returned,
            i.e. history will be fetched in reverse order *before* this message.
        :param locale: FunPay locale (``'en'`` / ``'uk'``).
            Defaults to ``''`` (Russian).
        """
        super().__init__(
            url='chat/history',
            locale=locale,
            data={'node': str(chat_id), 'last_message': str(before_message_id)},
            headers={'X-Requested-With': 'XMLHttpRequest'},
            parser_cls=MessagesParser,
            chat_id=chat_id,
            before_message_id=before_message_id,
            context={'chat_id': chat_id},
        )

    def parse_result(self, response: str) -> list[ParserMessage]:
        result = json.loads(response)
        messages = result['chat']['messages']
        html = '\n'.join(i['html'] for i in messages)
        return self.parser_cls(html, options=self.parser_options).parse()

    def transform_result(self, messages) -> list[Message]:
        return [
            Message.model_validate(i, context={'bot': self._bot} | self.context)
            for i in messages
        ]
