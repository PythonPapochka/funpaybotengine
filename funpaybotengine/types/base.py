from __future__ import annotations


__all__ = ('FunPayObject', 'FunPayMutableObject')

from typing import Any

from pydantic import BaseModel, ConfigDict, PrivateAttr
from funpayparsers.types import FunPayObject as PFunPayObject

from funpaybotengine.base import BindableObject


class FunPayObject(BindableObject, BaseModel, PFunPayObject):
    model_config = ConfigDict(
        frozen=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
        validate_default=True,
        from_attributes=True,
    )

    _cache_: dict[str, Any] = PrivateAttr(default_factory=dict)


class FunPayMutableObject(FunPayObject, BaseModel):
    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )
