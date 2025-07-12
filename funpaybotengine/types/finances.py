from __future__ import annotations


__all__ = ('TransactionPreview', 'Transaction', 'TransactionPreviewsBatch')


from typing import Annotated
from types import MappingProxyType
from collections.abc import Mapping

from pydantic import BaseModel, BeforeValidator
from funpayparsers.types import (
    Transaction as PTransaction,
    TransactionPreview as PTransactionPreview,
    TransactionPreviewsBatch as PTransactionPreviewsBatch,
)

from funpaybotengine.types.base import FunPayObject
from funpaybotengine.types.enums import PaymentMethod, TransactionStatus
from funpaybotengine.types.common import MoneyValue


class TransactionPreview(FunPayObject, BaseModel, PTransactionPreview):
    """Represents a transaction preview."""

    status: TransactionStatus
    """Transaction status."""

    amount: MoneyValue
    """Transaction amount."""

    payment_method: PaymentMethod | None
    """Payment method, if applicable."""


class Transaction(FunPayObject, BaseModel, PTransaction):
    status: TransactionStatus
    data: Annotated[
        Mapping[str, str], BeforeValidator(Transaction._convert_to_immutable)
    ]

    @staticmethod
    def _convert_to_immutable(value):
        return MappingProxyType(value)


class TransactionPreviewsBatch(FunPayObject, BaseModel, PTransactionPreviewsBatch):
    """
    Represents a single batch of transaction previews returned by FunPay.

    This batch contains a portion of all available transaction previews (typically 25),
    along with metadata required to fetch the next batch.
    """

    transactions: tuple[TransactionPreview, ...]
    """List of transaction previews included in this batch."""
