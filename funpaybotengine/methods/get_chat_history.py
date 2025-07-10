from __future__ import annotations


__all__ = ('GetChatHistory',)

import json

from pydantic import BaseModel
from funpayparsers.parsers import MessagesParser

from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.types.messages import Message


class GetChatHistory(FunPayMethod[list[Message]], BaseModel):
    chat_id: int | str
    last_message_id: int = 9999999999

    def __init__(self, chat_id: int | str, last_message_id: int = 9999999999):
        super().__init__(
            url='https://funpay.com/chat/history',
            data={'node': str(chat_id), 'last_message': str(last_message_id)},
            headers={'X-Requested-With': 'XMLHttpRequest'},
            parser_cls=MessagesParser,
            chat_id=chat_id,
            last_message_id=last_message_id,
        )

    def parse_result(self, response: str):
        result = json.loads(response)
        messages = result['chat']['messages']
        html = '\n'.join(i['html'] for i in messages)
        return self.parser_cls(html, options=self.parser_options).parse()

    def transform_result(self, messages) -> list[Message]:
        return [
            Message.model_validate(i.as_dict(), context={'bot': self._bot})
            for i in messages
        ]
