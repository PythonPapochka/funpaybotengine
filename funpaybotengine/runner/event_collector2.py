from __future__ import annotations


import time
from typing import TYPE_CHECKING, Any, Type, TypeVar, TypeAlias
from dataclasses import field, dataclass
from collections import defaultdict
from collections.abc import Callable

from funpaybotengine.dispatching import RunnerEvent
from funpaybotengine.utils import random_runner_tag
from funpaybotengine.types.enums import MessageType, OrderPreviewType
from funpaybotengine.runner.config import RunnerConfig
from funpaybotengine.dispatching.events.builtin_events import (
    OrderEvent,
    NewSaleEvent,
    NewMessageEvent,
    SaleClosedEvent,
    ChatChangedEvent,
    NewPurchaseEvent,
    SaleRefundedEvent,
    SaleReopenedEvent,
    PurchaseClosedEvent,
    PurchaseRefundedEvent,
    PurchaseReopenedEvent,
    SaleClosedByAdminEvent,
    PurchaseClosedByAdminEvent,
    SalePartiallyRefundedEvent,
    PurchasePartiallyRefundedEvent,
    SaleEvent,
    PurchaseEvent,
)
from funpaybotengine.types.requests.runner import NodeRequestObject, ChatBookmarksRequestObject
from funpaybotengine.storage.inmemory_storage import InMemoryStorage
from funpaybotengine.exceptions.session_exceptions import UnexpectedHTTPStatusError
from funpaybotengine.loggers import runner_logger as logger
from funpaybotengine.types.messages import Message


if TYPE_CHECKING:
    from funpaybotengine.client.bot import Bot
    from funpaybotengine.storage.base import Storage
    from funpaybotengine.types.orders import OrderPreview
    from funpaybotengine.types.updates import ChatNode, RunnerResponse, RunnerResponseObject


CHAT_EVENTS = ChatChangedEvent | NewMessageEvent


_KNOWN_ORDER_RELATED: dict[MessageType, tuple[Type[SaleEvent], Type[PurchaseEvent]]] = {
    MessageType.NEW_ORDER: (NewSaleEvent, NewPurchaseEvent),
    MessageType.ORDER_CLOSED: (SaleClosedEvent, PurchaseClosedEvent),
    MessageType.ORDER_CLOSED_BY_ADMIN: (SaleClosedByAdminEvent, PurchaseClosedByAdminEvent),
}

_UNKNOWN_ORDER_RELATED: dict[MessageType, tuple[Type[SaleEvent], Type[PurchaseEvent]]] = {
    MessageType.ORDER_REFUNDED: (SaleRefundedEvent, PurchaseRefundedEvent),
    MessageType.ORDER_PARTIALLY_REFUNDED: (
        SalePartiallyRefundedEvent,
        PurchasePartiallyRefundedEvent,
    ),
    MessageType.ORDER_REOPENED: (SaleReopenedEvent, PurchaseReopenedEvent),
}

_ORDER_RELATED = _KNOWN_ORDER_RELATED | _UNKNOWN_ORDER_RELATED


def resolve_order_event(message: Message) -> Type[OrderEvent] | None:
    if message.meta.type not in _KNOWN_ORDER_RELATED:
        return None

    if message.meta.type == MessageType.NEW_ORDER:
        seller = message.meta.buyer_id != message.bot.userid
    else:
        seller = message.meta.seller_id == message.bot.userid
    return _KNOWN_ORDER_RELATED[message.meta.type][0 if seller else 1]


F = TypeVar('F', bound=Callable[..., Any])


def attempts(amount: int = 0) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        async def inner(*args: Any, **kwargs: Any) -> Any:
            attempts = amount or float('inf')
            while attempts:
                attempts -= 1
                try:
                    return await func(*args, **kwargs)
                except UnexpectedHTTPStatusError:
                    if not attempts:
                        raise
        return inner  # type: ignore
    return decorator


EVENTS_DICT: TypeAlias = dict[ChatChangedEvent, dict[NewMessageEvent, list[OrderEvent]]]

class EventCollector:
    """
    Collects updates from FunPay and transforms them into update objects
    compatible with funpaybotengine.
    """

    def __init__(
        self,
        bot: Bot,
        config: RunnerConfig,
        *,
        session_storage: Storage | None = None,
    ) -> None:
        self.bot = bot
        self.config = config
        self.last_chats_request_timestamp: int | float = time.time()

        self.storage = self.bot.storage
        self.session_storage = session_storage or InMemoryStorage()

    @attempts()
    async def _get_chat_bookmarks(self) -> RunnerResponse:
        """
        Fetches chat bookmarks using runner.

        :return: ``RunnerResponse`` object with chat bookmarks.
        """
        return await self.bot.runner_request(objects_to_request=[ChatBookmarksRequestObject()])

    @attempts()
    async def _get_sales(self, order_id: str | None = None) -> tuple[OrderPreview, ...]:
        """
        Fetches last 100 sales.

        If an order ID is provided, only the matching sale is returned.
        """
        return (await self.bot.get_sales(order_id_filter=order_id)).orders

    @attempts()
    async def _get_purchases(self, order_id: str | None = None) -> tuple[OrderPreview, ...]:
        """
        Fetches last 100 purchases.

        If an order ID is provided, only the matching purchase is returned.
        """
        return (await self.bot.get_purchases(order_id_filter=order_id)).orders

    @attempts()
    async def _get_node(self, objs: list[NodeRequestObject]) -> RunnerResponse:
        return await self.bot.runner_request(objects_to_request=objs)

    @attempts()
    async def _get_chat_history(self, chat_id: int) -> list[Message]:
        return await self.bot.get_chat_history(chat_id=chat_id)

    async def get_chat_histories(
        self,
        chat_ids: list[int],
    ) -> dict[int, list[Message]]:
        """
        Fetches specified in ``chat_ids`` chat histories.

        :param chat_ids: List of chat IDs.
        :return: Dictionary in following format: `{node_id: runner response}`.
        """
        messages: dict[int, list[Message]] = {}

        if self.config.keep_unread:
            for i in chat_ids:
                messages |= {i: await self._get_chat_history(i)}
            return messages

        objs = [NodeRequestObject(chat_id=i, runner_tag=random_runner_tag()) for i in chat_ids]
        for i in range(0, len(objs), 10):
            result = await self._get_node(objs[i : i + 10])
            if not result.nodes:
                return {}
            messages.update({i.data.node.id: i.data.messages for i in result.nodes})
        return messages

    async def init_chats(self) -> None:
        logger.debug('Initializing chats...')
        result = await self._get_chat_bookmarks()
        self.last_chats_request_timestamp = result.timestamp

        if not result.chat_bookmarks:
            return

        for i in result.chat_bookmarks.data.chat_previews:
            logger.debug(
                f'Chat {i.id} ({i.username}) initialized. '
                f'Last message ID: {i.last_message_id}'
            )
            await self.session_storage.update_chat(i)

    async def get_chat_changed_events(self, runner_response: RunnerResponse) -> EVENTS_DICT:
        """
        Iterates over chat bookmarks in the runner response, compares each chat
        with the cached version in session storage, and generates ``ChatChangedEvent`` objects.

        A chat is considered changed if its ``ChatPreview.last_message_id`` differs between
        the runner response and the session storage, or if the chat is missing from
        the session storage entirely.

        :return: A list of ``ChatChangedEvent`` objects.
        """
        result: EVENTS_DICT = {}

        logger.debug('Getting changed chats...')
        if not runner_response.chat_bookmarks:
            return result

        for chat_preview in reversed(runner_response.chat_bookmarks.data.chat_previews):
            cached_chat = await self.session_storage.get_chat(chat_preview.id)

            if cached_chat and cached_chat.last_message_id == chat_preview.last_message_id:
                logger.debug(
                    f'Chat {chat_preview.id} ({chat_preview.username}) '
                    f'hasn\'t changed since last runner request.'
                )
                continue

            logger.debug(
                f'Chat {chat_preview.id} ({chat_preview.username}) '
                f'has changed since last runner request: '
                f'{cached_chat.last_message_id if cached_chat is not None else 0} -> '
                f'{chat_preview.last_message_id}.'
            )
            event = ChatChangedEvent(
                previous=cached_chat,
                object=chat_preview,
                tag=runner_response.chat_bookmarks.tag,
            ).as_(self.bot)

            result[event] = {}
        return result

    async def get_new_message_events(self, events: EVENTS_DICT) -> EVENTS_DICT:
        """
        Fetches chat histories for each ``ChatChangedEvent`` in the ``events`` list, identifies
        new messages and generates ``NewMessageEvent`` objects.

        If ``ChatChangedEvent.previous`` is ``None`` (i.e., the session storage did not contain
        a ``PrivateChatPreview`` object for the chat), messages are considered new if their
        timestamp is later than the previous chat bookmarks request
        and their ID is less than or equal to ``ChatChangedEvent.object.last_message_id``.

        Otherwise, messages are considered new if their IDs are greater than
        ``ChatChangedEvent.previous.last_message_id`` and less than or equal to
        ``ChatChangedEvent.object.last_message_id``.

        :param events: A list of ``ChatChangedEvent`` objects.
        :return: A list of ``NewMessageEvent`` objects.
        """
        chat_changed_events = {e.object.id: e for e in events.keys()}
        logger.debug(f'Getting new messages for chats '
                     f'{", ".join(str(i) for i in chat_changed_events)}.')
        chat_histories = await self.get_chat_histories(list(chat_changed_events.keys()))

        for event, dict_ in events.items():
            logger.debug(f'Processing chat {event.chat_preview.id}...')
            from_id = event.previous.last_message_id if event.previous else 0
            to_id = event.object.last_message_id

            for message in chat_histories[chat_id]:
                if from_id != 0 and from_id < message.id <= to_id:
                    logger.debug(
                        f'New message in chat {chat_id}: {message.id} '
                        f'(from IDs difference).'
                    )
                    events.total.insert(insert, NewMessageEvent(object=message, tag=None))
                    offset += 1
                elif message.timestamp >= self.last_chats_request_timestamp and message.id <= to_id:
                    logger.debug(
                        f'New message in chat {chat_id}: {message.id} '
                        f'(from timestamp difference: '
                        f'{message.timestamp} >= {self.last_chats_request_timestamp}).'
                    )
                    events.total.insert(insert, NewMessageEvent(object=message, tag=None))
                    offset += 1
        return result