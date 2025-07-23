from __future__ import annotations


__all__ = ('Event', 'RunnerEvent', 'BotEngineEvent', 'ExceptionEvent')


from typing import Any, Generic, TypeVar

from funpaybotengine.base import BindableObject


EventObject = TypeVar('EventObject', bound=Any)


class Event(BindableObject, Generic[EventObject]):
    def __init__(self, obj: EventObject) -> None:
        super().__init__()

        self._object: EventObject = obj
        self._data: dict[Any, Any] = {}
        self._propagation_stopped: bool = False

    def __setitem__(self, key: Any, value: Any) -> None:
        self._data[key] = value

    def __getitem__(self, key: Any) -> Any:
        return self._data[key]

    def get(self, key: Any) -> Any:
        return self._data.get(key, None)

    def stop_propagation(self) -> None:
        self._propagation_stopped = True

    @property
    def object(self) -> EventObject:
        return self._object

    @property
    def propagation_stopped(self) -> bool:
        return self._propagation_stopped


class RunnerEvent(Event[EventObject], Generic[EventObject]):
    def __init__(self, obj: EventObject, tag: str) -> None:
        super().__init__(obj=obj)

        self._tag = tag

    @property
    def tag(self) -> str:
        return self._tag


class BotEngineEvent(Event[EventObject], Generic[EventObject]):
    def __init__(self, obj: EventObject) -> None:
        super().__init__(obj)


class ExceptionEvent(BotEngineEvent[Any]):
    def __init__(self, obj: Event[Any], exception: Exception) -> None:
        super().__init__(obj=obj)

        self._exception = exception


    @property
    def exception(self) -> Exception:
        return self._exception
