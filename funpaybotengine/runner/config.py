from __future__ import annotations


__all__ = ('RunnerConfig',)


from typing import Literal

from dataclasses import dataclass


@dataclass
class RunnerConfig:
    interval: int | float = 4.0
    """
    Interval between updates requests.
    Must be more than ``0``.
    
    Defaults to ``4.0``.
    """

    initial_messages_discover_mode: Literal['heading', 'number', 'time'] = 'heading'
    max_initial_messages_amount: int = 10
    max_initial_message_time: int = 3600

    discover_sales: bool = True
    discover_purchases: bool = True
