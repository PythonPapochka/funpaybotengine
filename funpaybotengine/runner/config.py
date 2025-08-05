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

    discover_sales: bool = True
    discover_purchases: bool = True
