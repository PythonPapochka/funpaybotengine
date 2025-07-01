from pydantic import BaseModel
from funpaybotengine.base import BindableObject
from typing import Generic, TypeVar, Any


class FunPayObject(BindableObject, BaseModel):
    raw_source: str
