from __future__ import annotations

__all__ = ('Dispatcher', )


from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .base import Router


class Dispatcher(Router):
    ...

