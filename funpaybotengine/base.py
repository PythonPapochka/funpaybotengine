from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar, ParamSpec, Concatenate
from collections.abc import Callable

from pydantic import BaseModel, PrivateAttr
from typing_extensions import Self


if TYPE_CHECKING:
    from funpaybotengine.client.bot import Bot


P = ParamSpec('P')
T = TypeVar('T', bound='BindableObject')
R = TypeVar('R')


class BindableObject(BaseModel):
    _bot: Bot | None = PrivateAttr()

    def model_post_init(self, context: dict[Any, Any]) -> None:
        self._bot = context.get('bot') if context else None

    def as_(self, bot: Bot | None, /) -> Self:
        self.bind_to(bot)
        return self

    def unbind(self) -> None:
        self._bot = None

    def bind_to(self, bot: Bot | None, /) -> None:
        self._bot = bot

    @property
    def bot(self) -> Bot | None:
        return self._bot


def check_bound(func: Callable[Concatenate[T, P], R]) -> Callable[Concatenate[T, P], R]:
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
