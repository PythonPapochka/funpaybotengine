__all__ = ('FunPayObject', )

from pydantic import BaseModel, ConfigDict
from funpaybotengine.base import BindableObject


class FunPayObject(BindableObject, BaseModel):
    model_config = ConfigDict(
        frozen=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    raw_source: str
