__all__ = ('FunPayMethod', 'MethodReturnType')

from pydantic import BaseModel, Field
from funpaybotengine.base import BindableObject
from typing import Generic, TypeVar, Any, Type
from funpayparsers.parsers.base import FunPayObjectParser, ParsingOptions
from http import HTTPMethod, HTTPStatus
from abc import ABC, abstractmethod


MethodReturnType = TypeVar('MethodReturnType', bound=Any)


class FunPayMethod(BindableObject, BaseModel, Generic[MethodReturnType], ABC):
    url: str
    method: HTTPMethod = HTTPMethod.GET
    headers: dict[str, str] = Field(default_factory=dict)
    data: dict[str, str] = Field(default_factory=dict)
    expected_status_codes: list[int | HTTPStatus] = [HTTPStatus.OK]

    parser_cls: Type[FunPayObjectParser] | None = None
    parser_options: ParsingOptions | None = None

    timeout: int | float = 10.0

    def model_post_init(self, context: Any, /) -> None:
        super(BindableObject, self).model_post_init(context)
        if self.parser_cls and self.parser_options is None:
            self.parser_options = self.parser_cls.get_options_cls()()

    def parse_result(self, response: str):  # todo: response is not a str, but Response obj. Implement Response obj.
        if self.parser_cls is None:
            return response

        return self.parser_cls(response, options=self.parser_options).parse()

    @abstractmethod
    def transform_result(self, result: Any) -> MethodReturnType: ...
