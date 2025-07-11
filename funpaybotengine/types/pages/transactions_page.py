from __future__ import annotations


__all__ = ('TransactionsPage',)


from pydantic import BaseModel
from funpayparsers.types.common import MoneyValue
from funpayparsers.types.finances import TransactionPreviewsBatch
from funpayparsers.types.pages.base import FunPayPage


class TransactionsPage(FunPayPage, BaseModel):
    """Represents the transactions page (https://funpay.com/account/balance)."""

    rub_balance: MoneyValue | None
    """RUB balance."""

    usd_balance: MoneyValue | None
    """USD balance."""

    eur_balance: MoneyValue | None
    """EUR balance."""

    transactions: TransactionPreviewsBatch | None
    """Transaction previews."""
