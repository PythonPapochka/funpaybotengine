from __future__ import annotations


__all__ = (
    'RequestableObject',
    'OrdersCountersRequestObject',
    'ChatCounterRequestObject',
    'ChatBookmarksRequestObject',
    'CPURequestObject',
    'RequestNodeInfo',
    'NodeRequestObject',
    'Action',
    'ActionNodeInfo',
    'SendMessageAction',
    'RunnerRequestData',
)
import json
from typing import Literal
from abc import ABC, abstractmethod

from pydantic import BaseModel, computed_field, Field, AliasChoices

from funpaybotengine.base import BindableObject


class RequestableObject(ABC, BaseModel):
    """
    Base class for all objects that can be sent as runner requests.
    """

    @computed_field
    @abstractmethod
    def type(self) -> str: ...

    """Request type identifier."""


class OrdersCountersRequestObject(RequestableObject, BaseModel):
    """
    Request for retrieving order counters of a specific user.
    """

    id: int
    """User ID whose order counters are being requested."""

    runner_tag: str = Field(
        serialization_alias='tag',
        validation_alias=AliasChoices('runner_tag', 'tag')
    )
    """Runner tag used for request tracking."""

    @computed_field
    def type(self) -> str:
        return 'orders_counters'

    @computed_field
    def data(self) -> bool:
        return False


class ChatCounterRequestObject(RequestableObject, BaseModel):
    """
    Request for retrieving chat counter for a user.
    """

    id: int
    """User ID whose chat counter is being requested."""

    runner_tag: str = Field(
        serialization_alias='tag',
        validation_alias=AliasChoices('runner_tag', 'tag')
    )
    """Runner tag used for request tracking."""

    @computed_field
    def type(self) -> str:
        return 'chat_counter'

    @computed_field
    def data(self) -> bool:
        return False


class CPURequestObject(RequestableObject, BaseModel):
    """
    Request for information about the offer currently being viewed by a user.
    """

    id: int
    """User ID whose currently viewed offer info is being requested."""

    runner_tag: str = Field(
        serialization_alias='tag',
        validation_alias=AliasChoices('runner_tag', 'tag')
    )
    """Runner tag used for request tracking."""

    @computed_field
    def type(self) -> str:
        return 'c-p-u'

    @computed_field
    def data(self) -> bool:
        return False


class ChatBookmarksRequestObject(RequestableObject, BaseModel):
    """
    Request for retrieving chat bookmarks for a user.
    """

    id: int
    """User ID whose chat bookmarks are being requested."""

    runner_tag: str = Field(
        serialization_alias='tag',
        validation_alias=AliasChoices('runner_tag', 'tag')
    )
    """Runner tag used for request tracking."""

    data: list[tuple[int, int]] | Literal[False] = False
    """
    Optional list of (chat ID, last message ID) pairs.

    If not provided, defaults to ``False`` (recommended).
    """

    @computed_field
    def type(self) -> str:
        return 'chat_bookmarks'


class RequestNodeInfo(BaseModel):
    """
    Chat node metadata used in ``NodeRequestObject.data``.
    """

    chat_id: int | str = Field(
        serialization_alias='node',
        validation_alias=AliasChoices('chat_id', 'node')
    )
    """Chat ID or name whose message history is being requested."""

    after_message_id: int = Field(
        default=0,
        serialization_alias='last_message',
        validation_alias=AliasChoices('after_message_id', 'last_message ')
    )
    """
    ID of the last message (start point for history retrieval).

    Fetches messages sent **after** this ID, typically in batches of 50.
    
    If you need to fetch last messages in a chat, set it to ``0``.
    """

    show_avatar: Literal[0, 1] = 1
    """
    Whether to include user avatars in the rendered HTML output.
    
    Avatars are only available for public chats.
    """

    @computed_field
    def content(self) -> str:
        return ''


class NodeRequestObject(RequestableObject, BaseModel):
    """
    Request for retrieving chat (node) message history.
    """

    chat_id: int | str = Field(
        serialization_alias='id',
        validation_alias=AliasChoices('chat_id', 'id')
    )
    """Chat ID or name whose history is being requested."""

    runner_tag: str = Field(
        serialization_alias='tag',
        validation_alias=AliasChoices('runner_tag', 'tag')
    )
    """Runner tag used for request tracking."""

    data: RequestNodeInfo | Literal[False] = False
    """
    Chat metadata describing what history to fetch.
    
    Set to ``False`` to retrieve the latest 50 messages from the chat.
    
    Defaults to ``False``.
    """

    @computed_field
    def type(self) -> str:
        return 'chat_node'


class Action(ABC, BaseModel):
    """
    Base class for all runner actions.
    """

    @computed_field
    @abstractmethod
    def action(self) -> str: ...

    """Action type identifier."""


class ActionNodeInfo(BaseModel):
    """
    Chat node metadata used in ``SendMessageAction.data``.
    """

    chat_id: int | str = Field(
        serialization_alias='node',
        validation_alias=AliasChoices('chat_id', 'node')
    )
    """Chat ID or name where the message should be sent."""

    after_message_id: int = Field(
        default=99999999999,
        serialization_alias='last_message',
        validation_alias=AliasChoices('after_message_id', 'last_message')
    )
    """Unused field (currently has no effect)."""

    message_text: str = Field(
        default='',
        serialization_alias='content',
        validation_alias=AliasChoices('message_text', 'content')
    )
    """
    Text content of the message.

    Leave empty when sending an image.
    """

    image_id: int | None = None
    """
    ID of the image to send.

    Leave as ``None`` if sending a text message.
    """


class SendMessageAction(Action, BaseModel):
    """
    Action that sends a message to a chat.
    """

    message_data: ActionNodeInfo = Field(
        serialization_alias='data',
        validation_alias=AliasChoices('message_data', 'data')
    )
    """Chat metadata for message delivery."""

    @computed_field
    def action(self) -> str:
        return 'chat_message'


class RunnerRequestData(BindableObject, BaseModel):
    """
    Payload structure for requests sent to https://funpay.com/runner/.
    """

    requested_objects: list[RequestableObject] | Literal[False] = Field(
        default=False,
        serialization_alias='objects',
        validation_alias=AliasChoices('objects', 'requested_objects')
    )
    """
    Optional list of objects to request (or ``False`` if none).
    
    Defaults to ``False``.
    """

    action: Action | Literal[False] = Field(
        default=False,
        serialization_alias='request',
        validation_alias=AliasChoices('request', 'action')
    )
    """
    Optional action to perform (e.g., send message).
    
    Defaults to ``False``.
    """

    csrf_token: str | None = None
    """
    Bot CSRF token.

    Defaults to ``None``.
    """

    def serialize_as_request_data(self) -> dict[str, str | None]:
        """Returns a dictionary suitable for runner HTTP requests."""
        return {
            'objects': json.dumps(
                [i.model_dump(exclude_none=True, by_alias=True) for i in self.requested_objects]
            )
            if self.requested_objects
            else 'false',
            'request': self.action.model_dump_json(exclude_none=True, by_alias=True)
            if self.action
            else 'false',
            'csrf_token': self.csrf_token,
        }
