from __future__ import annotations


__all__ = ('TransactionPreview', 'Transaction', 'TransactionPreviewsBatch')


from typing import TYPE_CHECKING

from funpaybotengine.types.base import FunPayObject


if TYPE_CHECKING:
    from funpaybotengine.types.enums import PaymentMethod, TransactionStatus
    from funpaybotengine.types.common import MoneyValue


class TransactionPreview(FunPayObject):
    """Represents a transaction preview."""

    id: int
    """Unique transaction ID."""

    date_text: str
    """Transaction date (as human-readable text)."""

    desc: str
    """Transaction description."""

    status: TransactionStatus
    """Transaction status."""

    amount: MoneyValue
    """Transaction amount."""

    payment_method: PaymentMethod | None
    """Payment method, if applicable."""

    withdrawal_number: str | None
    """Withdrawal card / phone / wallet number, if applicable."""


class Transaction(FunPayObject):
    status: TransactionStatus
    data: dict[str, str]


class TransactionPreviewsBatch(FunPayObject):
    """
    Represents a single batch of transaction previews returned by FunPay.

    This batch contains a portion of all available transaction previews (typically 25),
    along with metadata required to fetch the next batch.
    """

    transactions: list[TransactionPreview]
    """List of transaction previews included in this batch."""

    user_id: int | None
    """ID of the user to whom all transactions in this batch belong."""

    filter: str | None
    """
    The current filter applied to the review list.

    Known values:
        - ``''`` (empty string): no filter applied
        - ``'payment'``: payment transactions only
        - ``'withdraw'``: withdrawal transactions only
        - ``'order'``: order transactions only
        - ``'other'``: other transactions only
    """

    next_transaction_id: int | None
    """
    ID of the next transaction to use as a cursor for pagination.

    If present, this value should be included in the next request to fetch
    the following batch of transaction previews. 
    
    If ``None``, there are no more transactions to load.
    """
