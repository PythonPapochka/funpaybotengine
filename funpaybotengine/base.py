from funpaybotengine.client.bot import Bot


class BindableObject:
    def __init__(self, bot: Bot | None = None) -> None:
        self._bot = bot

    def as_(self, bot: Bot, /) -> 'BindableObject':
        self.bind_to(bot)
        return self

    def unbind(self) -> None:
        self._bot = None

    def bind_to(self, bot: Bot, /) -> None:
        if not isinstance(bot, Bot):
            raise TypeError(f'{bot} is not a bot instance.')
        self._bot = bot

    @property
    def bot(self) -> Bot | None:
        return self._bot


def check_bound(func):
    """
    Decorator for instance methods to ensure the object is bound to any Bot instance.
    """
    def wrapper(self: BindableObject, *args, **kwargs):
        if not isinstance(self, BindableObject):
            raise Exception('Not a bindable object.')  # todo: exceptions
        if self.bot is None:
            raise Exception(f'{self} is not bound to any bot.')
        return func(self, *args, **kwargs)
    return wrapper
