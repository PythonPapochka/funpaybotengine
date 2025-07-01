__all__ = ('OrdersCounters',
           'ChatBookmarks',
           'ChatCounter',
           'NodeInfo',
           'CurrentlyViewingOfferInfo',
           'ChatNode',
           'ActionResponse',
           'UpdateObject',
           'Updates')

from typing import Generic, TypeVar

from funpaybotengine.types.base import FunPayObject
from funpaybotengine.types.chat import PrivateChatPreview
from funpaybotengine.types.messages import Message
from funpaybotengine.types.enums import UpdateType
from pydantic import BaseModel


UpdateData = TypeVar('UpdateData')


# ------ Simple objects ------
class OrdersCounters(FunPayObject, BaseModel):
    """
    Represents an order counters data from updates object.
    """

    purchases: int
    """Active purchases amount (`buyer` field)."""
    sales: int
    """Active sales amount (`seller` field)."""


class ChatBookmarks(FunPayObject, BaseModel):
    """
    Represents a chat bookmarks data from updates object.
    """

    counter: int
    """Unread chats amount."""

    message: int
    """
    ID of the latest unread message.
    If there are new messages in multiple chats, this field contains the ID of the most recent message among all of them.
    """

    order: list[int]
    """Order of chat previews (list of chats IDs)."""

    chat_previews: list[PrivateChatPreview]
    """List of chat previews."""


class ChatCounter(FunPayObject, BaseModel):
    """
    Represents a chat counter data from updates object.
    """

    counter: int
    """Unread chats amount."""

    message: int
    """
    ID of the latest unread message.
    If there are new messages in multiple chats, this field contains the ID of the most recent message among all of them.
    """


# ------ C-P-U ------
class CurrentlyViewingOfferInfo(FunPayObject, BaseModel):
    id: int | str
    name: str


# ------ Nodes ------
class NodeInfo(FunPayObject, BaseModel):
    id: int
    name: str
    silent: bool


class ChatNode(FunPayObject, BaseModel):
    node: NodeInfo
    messages: list[Message]
    has_history: bool


# ------ Response to action ------
class ActionResponse(FunPayObject, BaseModel):
    """
    Represents an action response data from updates object.
    """

    error: str | None
    """Error text, if an error occurred while processing a request."""


class UpdateObject(FunPayObject, BaseModel, Generic[UpdateData]):
    """
    Represents a single update data from updates object.
    """

    type: UpdateType
    """Update type."""

    id: int | str  # todo: wtf is this? tag = id
    """Update ID."""

    tag: str
    """Update tag."""

    data: UpdateData
    """Update data."""


class Updates(FunPayObject, BaseModel):
    """
    Represents an updates object, returned by runner.
    """

    orders_counters: UpdateObject[OrdersCounters] | None
    chat_counter: UpdateObject[ChatCounter] | None
    chat_bookmarks: UpdateObject[ChatBookmarks] | None
    cpu: UpdateObject[CurrentlyViewingOfferInfo] | None
    nodes: list[UpdateObject[NodeInfo]] | None
    unknown_objects: list[dict] | None
    response: ActionResponse | None
