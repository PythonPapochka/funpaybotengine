from __future__ import annotations


__all__ = ('EventCollector',)


import time
from typing import TYPE_CHECKING, Any, Type, TypeVar
from dataclasses import field, dataclass
from collections import defaultdict
from collections.abc import Callable

from funpaybotengine.utils import random_runner_tag
from funpaybotengine.types.enums import MessageType, OrderPreviewType
from funpaybotengine.runner.config import RunnerConfig
from funpaybotengine.dispatching.events import (
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
)
from funpaybotengine.types.requests.runner import NodeRequestObject, ChatBookmarksRequestObject
from funpaybotengine.storage.inmemory_storage import InMemoryStorage
from funpaybotengine.exceptions.session_exceptions import UnexpectedHTTPStatusError


if TYPE_CHECKING:
    from funpaybotengine.client.bot import Bot
    from funpaybotengine.storage.base import Storage
    from funpaybotengine.types.orders import OrderPreview
    from funpaybotengine.types.updates import ChatNode, RunnerResponse, RunnerResponseObject


CHAT_EVENTS = ChatChangedEvent | NewMessageEvent

_ORDER_RELATED_MESSAGE_TYPES: dict[MessageType, tuple[Type[OrderEvent], Type[OrderEvent]]] = {
    MessageType.NEW_ORDER: (NewSaleEvent, NewPurchaseEvent),
    MessageType.ORDER_CLOSED: (SaleClosedEvent, PurchaseClosedEvent),
    MessageType.ORDER_CLOSED_BY_ADMIN: (SaleClosedByAdminEvent, PurchaseClosedByAdminEvent),
    MessageType.ORDER_REFUNDED: (SaleRefundedEvent, PurchaseRefundedEvent),
    MessageType.ORDER_PARTIALLY_REFUNDED: (
        SalePartiallyRefundedEvent,
        PurchasePartiallyRefundedEvent,
    ),
    MessageType.ORDER_REOPENED: (SaleReopenedEvent, PurchaseReopenedEvent),
}


F = TypeVar('F', bound=Callable[..., Any])


def attempts(amount: int = 0) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        async def inner(*args: Any, **kwargs: Any) -> Any:
            attempts = amount or float('inf')
            error: Exception = Exception()
            while attempts:
                attempts -= 1
                try:
                    return await func(*args, **kwargs)
                except UnexpectedHTTPStatusError as e:
                    error = e
            else:
                raise error

        return inner  # type: ignore

    return decorator


@dataclass
class OrderRelatedMessages:
    """
    Container for order related messages.
    For internal use only.
    """

    sales: list[NewMessageEvent] = field(default_factory=list)
    """Sales related messages."""

    purchases: list[NewMessageEvent] = field(default_factory=list)
    """Purchases related messages."""

    unknown: list[NewMessageEvent] = field(default_factory=list)
    """Order-related messages with unknown type.

    These messages are related to orders but it is unclear whether they correspond
    to sales or purchases, since they lack any seller or buyer information and
    only contain the order ID.
    
    This list includes messages of types:
    
    - ``MessageType.ORDER_REFUNDED``
    - ``MessageType.ORDER_PARTIALLY_REFUNDED``
    - ``MessageType.ORDER_REOPENED``
    """


class EventCollector:
    """
    Collects updates from FunPay and transforms them into update objects
    compatible with funpaybotengine.
    """

    def __init__(
        self,
        bot: Bot,
        config: RunnerConfig,
        storage: Storage,
        *,
        session_storage: Storage | None = None,
    ) -> None:
        self.bot = bot
        self.config = config
        self.last_chats_request_timestamp: int | float = time.time()
        self.storage = storage
        self.session_storage = session_storage or InMemoryStorage()

    async def init_chats(self) -> None:
        result = await self.get_chat_bookmarks()
        self.last_chats_request_timestamp = result.timestamp

        if not result.chat_bookmarks:
            return

        for i in result.chat_bookmarks.data.chat_previews:
            await self.session_storage.update_chat(i)

    @attempts()
    async def get_chat_bookmarks(self) -> RunnerResponse:
        """
        Fetches chat bookmarks using runner.

        :return: ``RunnerResponse`` object with chat bookmarks.
        """
        chats = ChatBookmarksRequestObject(id=self.bot.userid, runner_tag=random_runner_tag())
        result = await self.bot.runner_request(requested_objects=[chats])
        return result

    @attempts()
    async def get_sales(self, order_id: str | None = None) -> tuple[OrderPreview, ...]:
        """
        Fetches last 100 sales.

        If an order ID is provided, only the matching sale is returned.
        """
        return (await self.bot.get_sales(order_id_filter=order_id)).orders

    @attempts()
    async def get_purchases(self, order_id: str | None = None) -> tuple[OrderPreview, ...]:
        """
        Fetches last 100 purchases.

        If an order ID is provided, only the matching purchase is returned.
        """
        return (await self.bot.get_purchases(order_id_filter=order_id)).orders

    async def get_chat_histories(
        self, chat_ids: list[int],
    ) -> dict[int, RunnerResponseObject[ChatNode]]:
        """
        Fetches specified in ``chat_ids`` chat histories.
        """
        nodes = {}
        objs = [NodeRequestObject(chat_id=i, runner_tag=random_runner_tag()) for i in chat_ids]

        for i in range(0, len(objs), 10):
            result = await self._get_node(objs[i : i + 10])

            if not result.nodes:
                return {}

            nodes.update({i.data.node.id: i for i in result.nodes})
        return nodes

    @attempts()
    async def _get_node(self, objs: list[NodeRequestObject]) -> RunnerResponse:
        return await self.bot.runner_request(requested_objects=objs)

    async def get_chat_changed_events(
        self, runner_response: RunnerResponse,
    ) -> list[ChatChangedEvent]:
        """
        Iterates over chat bookmarks in the runner response, compares each chat
        with the cached version in session storage, and generates ``ChatChangedEvent`` objects.

        A chat is considered changed if its ``ChatPreview.last_message_id`` differs between
        the runner response and the session storage, or if the chat is missing from
        the session storage entirely.

        :return: A list of ``ChatChangedEvent`` objects.
        """
        if not runner_response.chat_bookmarks:
            return []

        result = []

        for chat_preview in reversed(runner_response.chat_bookmarks.data.chat_previews):
            cached_chat = await self.session_storage.get_chat(chat_preview.id)

            if cached_chat == chat_preview:
                continue

            result.append(
                ChatChangedEvent(
                    previous=cached_chat,
                    object=chat_preview,
                    tag=runner_response.chat_bookmarks.tag,
                ).as_(self.bot),
            )

        return result

    async def get_new_message_events(
        self, events: list[ChatChangedEvent],
    ) -> list[NewMessageEvent]:
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
        chat_changed_events = {e.object.id: e for e in events}
        nodes = await self.get_chat_histories([e.object.id for e in events])

        result: list[NewMessageEvent] = []
        for chat_id, event in chat_changed_events.items():
            node = nodes[chat_id]
            from_id = event.previous.last_message_id if event.previous else 0
            to_id = event.object.last_message_id

            for message in node.data.messages:
                if from_id != 0 and from_id < message.id <= to_id:
                    result.append(NewMessageEvent(object=message, tag=node.tag))
                elif (
                    message.timestamp >= self.last_chats_request_timestamp and message.id <= to_id
                ):
                    result.append(NewMessageEvent(object=message, tag=node.tag))

        return result

    async def get_order_related_messages(
        self, events: list[NewMessageEvent],
    ) -> OrderRelatedMessages:
        """
        Searches for order related message in the ``events`` list, determines whether it is the
        sale or the purchase and stores them into ``OrderRelatedMessages`` object.

        - ``MessageType.NEW_ORDER``
        - ``MessageType.ORDER_REFUNDED``
        - ``MessageType.ORDER_PARTIALLY_REFUNDED``
        - ``MessageType.ORDER_CLOSED``
        - ``MessageType.ORDER_CLOSED_BY_ADMIN``
        - ``MessageType.ORDER_REOPENED``

        :param events: list of ``NewMessageEvent`` objects.
        :return: ``OrderRelatedMessages`` object.
        """
        r = OrderRelatedMessages()
        for e in events:
            meta = e.object.meta
            if meta.type not in _ORDER_RELATED_MESSAGE_TYPES:
                continue

            if meta.buyer_id:
                r.purchases.append(e) if meta.buyer_id == self.bot.userid else r.sales.append(e)
            elif meta.seller_id:
                r.sales.append(e) if meta.seller_id == self.bot.userid else r.purchases.append(e)
            else:
                r.unknown.append(e)
        return r

    async def resolve_unknown_message(
        self,
        message: NewMessageEvent,
        messages: OrderRelatedMessages,
        sales: dict[str, OrderPreview],
        purchases: dict[str, OrderPreview],
    ) -> None:
        """
        Determines whether an unknown order-related message refers to a sale or a purchase.

        Extracts the order ID from ``NewMessageEvent.object.meta.order_id`` and tries to match it
        against the provided ``sales`` and ``purchases`` dictionaries.
        If a matching ``OrderPreview`` is found, the message is classified based on the dictionary
        it was found in.

        If not found in the dictionaries, the method attempts to fetch the preview
        from the bot's storage.
        If the retrieved preview exists and its type is not ``OrderType.UNKNOWN``,
        the message is classified accordingly, and the preview is added to the appropriate
        **passed** dictionary (``sales`` or ``purchases``).

        If the preview is still not found, FunPay is queried:
            - If ``self.config.discover_sales`` is enabled,
            the sales list is queried using the order ID filter.

            - If ``self.config.discover_purchases`` is enabled,
            the purchases list is queried using the same filter.

        If a preview is found during this step, it updated in bot storage
        and also added to the corresponding dictionary.

        Once the message type is determined, it is copied from
        ``OrderRelatedMessages.unknown`` to the appropriate list
        (``OrderRelatedMessages.sales`` or ``OrderRelatedMessages.purchases``).

        :param message: The message to resolve.
        :param messages: Container holding order-related messages.
        :param sales: Dictionary of known sales, keyed by order ID.
        :param purchases: Dictionary of known purchases, keyed by order ID.
        """
        if message.object.meta.order_id in purchases:
            messages.purchases.append(message)
            return
        if message.object.meta.order_id in sales:
            messages.sales.append(message)
            return

        saved_order = await self.storage.get_order(message.object.meta.order_id)  # type: ignore[arg-type]
        if saved_order and saved_order.type is not OrderPreviewType.UNKNOWN:
            if saved_order.type is OrderPreviewType.PURCHASE:
                messages.purchases.append(message)
                purchases[saved_order.id] = saved_order
            elif saved_order.type is OrderPreviewType.SALE:
                messages.sales.append(message)
                sales[saved_order.id] = saved_order
            return

        if self.config.discover_sales:
            order_preview = await self.get_sales(order_id=message.object.meta.order_id)
            if order_preview:
                messages.sales.append(message)
                sales[order_preview[0].id] = order_preview[0]
                await self.storage.update_order(order_preview[0])
                return

        if self.config.discover_purchases:
            order_preview = await self.get_purchases(order_id=message.object.meta.order_id)
            if order_preview:
                messages.purchases.append(message)
                purchases[order_preview[0].id] = order_preview[0]
                await self.storage.update_order(order_preview[0])
                return

    async def make_order_events(self, messages: OrderRelatedMessages) -> list[OrderEvent]:
        """
        Creates order events from order related ``NewMessageEvent`` objects.
        """
        sales, purchases = {}, {}
        total_events: list[OrderEvent] = []

        if (messages.purchases or messages.unknown) and self.config.discover_purchases:
            purchases = {i.id: i for i in await self.get_purchases()}

        if (messages.sales or messages.unknown) and self.config.discover_sales:
            sales = {i.id: i for i in await self.get_sales()}

        for e in messages.unknown:
            await self.resolve_unknown_message(e, messages, sales, purchases)

        total_events.extend(await self._make_order_events(messages.sales, sales, True))
        total_events.extend(await self._make_order_events(messages.purchases, purchases, False))

        return total_events

    async def _make_order_events(
        self, messages: list[NewMessageEvent], orders: dict[str, OrderPreview], sales: bool = True,
    ) -> list[OrderEvent]:
        if not messages:
            return []

        result: list[OrderEvent] = []

        for e in messages:
            cls = _ORDER_RELATED_MESSAGE_TYPES[e.object.meta.type][0 if sales else 1]
            event: OrderEvent = cls(object=e.object, related_new_message_event=e, tag=e.tag)
            event._order_preview = orders.get(e.object.meta.order_id)  # type: ignore[arg-type]
            result.append(event)

        return result

    async def get_order_events(self, events: list[NewMessageEvent]) -> list[OrderEvent]:
        order_messages = await self.get_order_related_messages(events=events)
        return await self.make_order_events(order_messages)

    def merge_events(
        self,
        chat_changed_events: list[ChatChangedEvent],
        new_message_events: list[NewMessageEvent],
        order_events: list[OrderEvent],
    ) -> list[CHAT_EVENTS | OrderEvent]:
        """
        Merges chat-related and order-related events into a single, ordered sequence.

        For each ``ChatChangedEvent``, appends:
            1. The chat changed event itself.
            2. All ``NewMessageEvent`` instances related to that chat, in the order they appear.
            3. For each such ``NewMessageEvent``, if it is related to an order,
               the corresponding ``OrderEvent`` is appended immediately after it.

        This ensures a chronological and logical grouping of events by chat context,
        preserving the relationship between chat messages and their corresponding order actions.

        :param chat_changed_events: List of ``ChatChangedEvent`` objects.
        :param new_message_events: List of ``NewMessageEvent`` objects.
        :param order_events: List of order events.
        :return: Merged list of all events in the described order.
        """
        chat_id_to_messages: dict[int, list[NewMessageEvent]] = defaultdict(list)
        message_to_order: dict[NewMessageEvent, OrderEvent] = {}
        result: list[CHAT_EVENTS | OrderEvent] = []

        for i in new_message_events:
            chat_id_to_messages[i.object.chat_id].append(i)  # type: ignore[index]

        for j in order_events:
            message_to_order[j.related_new_message_event] = j

        for chat_changed_event in chat_changed_events:
            result.append(chat_changed_event)

            for new_message_event in chat_id_to_messages[chat_changed_event.object.id]:
                result.append(new_message_event)
                if message_to_order.get(new_message_event):
                    result.append(message_to_order[new_message_event])

        return result

    async def get_events(self) -> list[CHAT_EVENTS | OrderEvent]:
        """
        Fetches and processes all relevant chat and order-related events.

        This method:
            1. Retrieves the latest chat bookmarks from the runner.
            2. Determines which chats have changed since the last request.
            3. Fetches new message events based on changed chats.
            4. Builds order-related events from the new messages.
            5. Merges all events into a single chronological list.
            6. Binds each event to the current bot instance.
            7. Updates session and order storages with latest state.
            8. Updates the internal timestamp of the last successful chat sync.

        :return: A list of chat or order events to be handled by the bot.
        """
        runner_response = await self.get_chat_bookmarks()
        chat_changed_events = await self.get_chat_changed_events(runner_response)
        new_message_events = await self.get_new_message_events(chat_changed_events)
        order_events = await self.get_order_events(new_message_events)
        total = self.merge_events(chat_changed_events, new_message_events, order_events)

        for event in total:
            event.bind_to(self.bot)

        for i in chat_changed_events:
            await self.session_storage.update_chat(i.object)

        order_events_mapping = {}
        for j in order_events:
            if j._order_preview is None:
                continue
            order_events_mapping[j._order_preview.id] = j._order_preview

        for k in order_events_mapping.values():
            await self.storage.update_order(k)

        self.last_chats_request_timestamp = runner_response.timestamp or time.time()

        return total
