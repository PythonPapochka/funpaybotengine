from __future__ import annotations


__all__ = ('RunnerConfig',)


from typing import Literal, Annotated

from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class RunnerConfig:
    interval: Annotated[int | float, Field(gt=0)] = 3.0

    discover_new_messages: bool = True
    initial_messages_discover_mode: Literal['heading', 'number', 'time'] = 'heading'
    max_initial_messages_amount: int = 10
    max_initial_message_time: int = 3600

    discover_sales: bool = True
    link_sales_with_system_messages: bool = True
    delay_sale_event_if_no_message: bool = True

    discover_purchases: bool = True
    link_purchases_with_system_messages: bool = True
    delay_purchase_event_if_no_message: bool = True

    @property
    def link_sales_enabled(self) -> bool:
        return self.discover_new_messages and self.link_sales_with_system_messages

    @property
    def link_purchases_enabled(self) -> bool:
        return self.discover_new_messages and self.link_purchases_with_system_messages

    @property
    def delay_sales_enabled(self) -> bool:
        return self.link_sales_enabled and self.delay_sale_event_if_no_message

    @property
    def delay_purchases_enabled(self) -> bool:
        return self.link_purchases_enabled and self.delay_purchase_event_if_no_message