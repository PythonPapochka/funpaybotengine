from __future__ import annotations


__all__ = (
    'OrdersCounters',
    'ChatBookmarks',
    'ChatCounter',
    'NodeInfo',
    'ChatNode',
    'ActionResponse',
    'UpdateObject',
    'UpdatesPack',
)

from typing import TypeVar
from types import MappingProxyType
from collections.abc import Mapping

from pydantic import BaseModel, field_validator
from funpayparsers.types import (
    ChatNode as PChatNode,
    NodeInfo as PNodeInfo,
    ChatCounter as PChatCounter,
    UpdatesPack as PUpdatesPack,
    UpdateObject as PUpdateObject,
    ChatBookmarks as PChatBookmarks,
    ActionResponse as PActionResponse,
    OrdersCounters as POrdersCounters,
)

from funpaybotengine.types.base import FunPayObject
from funpaybotengine.types.chat import PrivateChatPreview
from funpaybotengine.types.enums import UpdateType
from funpaybotengine.types.common import CurrentlyViewingOfferInfo
from funpaybotengine.types.messages import Message


UpdateData = TypeVar('UpdateData')


# ------ Simple objects ------
class OrdersCounters(FunPayObject, BaseModel, POrdersCounters):
    """Represents an order counters data from updates object."""

    ...


class ChatBookmarks(FunPayObject, BaseModel, PChatBookmarks):
    """Represents a chat bookmarks data from updates object."""

    order: tuple[int, ...]
    """Order of chat previews (list of chats IDs)."""

    chat_previews: tuple[PrivateChatPreview, ...]
    """List of chat previews."""


class ChatCounter(FunPayObject, BaseModel, PChatCounter):
    """Represents a chat counter data from updates object."""

    ...


# ------ Nodes ------
class NodeInfo(FunPayObject, BaseModel, PNodeInfo): ...


class ChatNode(FunPayObject, BaseModel, PChatNode):
    node: NodeInfo
    messages: tuple[Message, ...]


# ------ Response to action ------
class ActionResponse(FunPayObject, BaseModel, PActionResponse):
    """Represents an action response data from updates object."""

    ...


# ------ Update obj ------
class UpdateObject(FunPayObject, BaseModel, PUpdateObject[UpdateData]):
    """Represents a single update data from updates object."""

    type: UpdateType
    """Update type."""

    data: UpdateData
    """Update data."""


class UpdatesPack(FunPayObject, BaseModel, PUpdatesPack):
    """Represents an updates object, returned by runner."""

    orders_counters: UpdateObject[OrdersCounters] | None
    chat_counter: UpdateObject[ChatCounter] | None
    chat_bookmarks: UpdateObject[ChatBookmarks] | None
    cpu: UpdateObject[CurrentlyViewingOfferInfo] | None
    nodes: tuple[UpdateObject[ChatNode], ...] | None
    unknown_objects: tuple[Mapping, ...] | None
    response: ActionResponse | None

    @field_validator('unknown_objects', mode='before')
    @classmethod
    def convert_to_immutable(cls, value):
        if value is None:
            return value

        return tuple(MappingProxyType(i) for i in value)
