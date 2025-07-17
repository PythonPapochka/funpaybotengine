from __future__ import annotations

from pydantic import BaseModel, PrivateAttr
from typing_extensions import Self
from typing import Any, TypeVar, ParamSpec, Concatenate
from collections.abc import Callable

from funpaybotengine.client.base_bot import BaseBot


P = ParamSpec('P')
T = TypeVar('T', bound='BindableObject')
R = TypeVar('R')


class BindableObject(BaseModel):
    _bot: BaseBot | None = PrivateAttr()

    def model_post_init(self, context: dict[Any, Any]) -> None:
        self._bot = context.get('bot') if context else None

    def as_(self, bot: BaseBot | None, /) -> Self:
        self.bind_to(bot)
        return self

    def unbind(self) -> None:
        self._bot = None

    def bind_to(self, bot: BaseBot | None, /) -> None:
        if not isinstance(bot, BaseBot | None):
            raise TypeError(f'{bot} is not a bot instance.')
        self._bot = bot

    @property
    def bot(self) -> BaseBot | None:
        return self._bot


def check_bound(
        func: Callable[Concatenate[T, P], R]
) -> Callable[Concatenate[T, P], R]:
    """
    Decorator for instance methods to ensure the object is bound to any Bot instance.
    """

    def wrapper(obj: T, /, *args: P.args, **kwargs: P.kwargs) -> R:
        if not isinstance(obj, BindableObject):
            raise Exception('Not a bindable object.')  # todo: exceptions
        if obj.bot is None:
            raise Exception(f'{obj} is not bound to any bot.')
        return func(obj, *args, **kwargs)

    return wrapper
