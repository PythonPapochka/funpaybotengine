__all__ = ('FunPayObject', )

from pydantic import BaseModel
from funpaybotengine.base import BindableObject


class FunPayObject(BindableObject, BaseModel):
    raw_source: str
