from __future__ import annotations


__all__ = ('Event', 'RunnerEvent', 'BotEngineEvent', 'ExceptionEvent')


from typing import Any, Generic, TypeVar

from pydantic import Field, BaseModel, PrivateAttr

from funpaybotengine.base import BindableObject


EventObject = TypeVar('EventObject', bound=Any)


class Event(BindableObject, BaseModel, Generic[EventObject]):
    model_config = {
        'arbitrary_types_allowed': True,
    }

    object: EventObject = Field(frozen=True)
    _data: dict[str, Any] = PrivateAttr(default_factory=dict)
    _propagation_stopped: bool = PrivateAttr(default=False)
    _flags: set[str] = PrivateAttr(default_factory=set)

    def __setitem__(self, key: Any, value: Any) -> None:
        self._data[key] = value

    def __getitem__(self, key: Any) -> Any:
        return self._data[key]

    def get(self, key: Any) -> Any:
        return self._data.get(key, None)

    def set_flag(self, flag: str) -> None:
        self._flags.add(flag)

    def unset_flag(self, flag: str) -> None:
        try:
            self._flags.remove(flag)
        except KeyError:
            pass

    def set_flags(self, *flags: str) -> None:
        for i in flags:
            self.set_flag(i)

    def unset_flags(self, *flags: str) -> None:
        for i in flags:
            self.unset_flag(i)

    def flag(self, flag: str) -> bool:
        return flag in self._flags

    def flags(self) -> tuple[str, ...]:
        return tuple(self._flags)

    def stop_propagation(self) -> None:
        self._propagation_stopped = True

    @property
    def propagation_stopped(self) -> bool:
        return self._propagation_stopped

    @property
    def workflow_dict(self) -> dict[str, Any]:
        return {}

    def __hash__(self) -> int:
        return id(self)


class RunnerEvent(Event[EventObject], BaseModel, Generic[EventObject]):
    tag: str = Field(frozen=True)


class BotEngineEvent(Event[EventObject], BaseModel, Generic[EventObject]): ...


class ExceptionEvent(BotEngineEvent[Exception]):
    event: Event[Any] = Field(frozen=True)
