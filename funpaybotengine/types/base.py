__all__ = ('FunPayObject', )

from pydantic import BaseModel, ConfigDict, Field
from funpaybotengine.base import BindableObject
from typing import Any


class FunPayObject(BindableObject, BaseModel):
    model_config = ConfigDict(
        frozen=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    raw_source: str
    _cache_: dict[str, Any] = Field(default_factory=dict,
                                    exclude=True,
                                    repr=False,)


class FunPayMutableObject(FunPayObject, BaseModel):
    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )
