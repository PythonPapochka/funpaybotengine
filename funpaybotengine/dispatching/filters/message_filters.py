from __future__ import annotations


__all__ = (
    'MessageTextFilter',
    'MessageSenderUsernameFilter',
    'MessageSenderIDFilter',
    'MessageHasImageFilter',
)


from typing import TYPE_CHECKING, Any

from .base import Filter


if TYPE_CHECKING:
    from funpaybotengine.types.messages import Message
    from funpaybotengine.dispatching.events.base import Event


class MessageTextFilter(Filter):
    def __init__(self, message_text: str, /):
        self.message_text = message_text

    async def __call__(self, event: Event[Message], *args: Any, **kwargs: Any) -> bool:
        return self.message_text == event.object.text


class MessageSenderUsernameFilter(Filter):
    def __init__(self, message_sender_username: str, /):
        self.message_sender_username = message_sender_username

    async def __call__(self, event: Event[Message], *args: Any, **kwargs: Any) -> bool:
        return self.message_sender_username == event.object.sender_username


class MessageSenderIDFilter(Filter):
    def __init__(self, sender_id: int, /):
        self.sender_id = sender_id

    async def __call__(self, event: Event[Message], *args: Any, **kwargs: Any) -> bool:
        return self.sender_id == event.object.sender_id


class MessageHasImageFilter(Filter):
    def __init__(self, has_image: bool, /):
        self.has_image = has_image

    async def __call__(self, event: Event[Message], *args: Any, **kwargs: Any) -> bool:
        return bool(event.object.image_url)


"""
class MessageTypeFilter(Filter):
    def __init__(self, message_type: ..., /):
        self.message_type = message_type

    async def __call__(self, event: Event[Message], *args: Any, **kwargs: Any) -> bool:
        raise NotImplementedError()  # todo
"""
