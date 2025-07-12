from __future__ import annotations


__all__ = ('FunPayObject', 'FunPayMutableObject')

from typing import Any

from pydantic import BaseModel, ConfigDict, PrivateAttr

from funpaybotengine.base import BindableObject


class FunPayObject(BindableObject, BaseModel):
    model_config = ConfigDict(
        frozen=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
        validate_default=True,
        from_attributes=True,
    )

    raw_source: str
    """
    Raw source of an object.
    Typically a HTML string, but in rare cases can be a JSON string.
    """

    _cache_: dict[str, Any] = PrivateAttr(default_factory=dict)


class FunPayMutableObject(FunPayObject, BaseModel):
    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )
