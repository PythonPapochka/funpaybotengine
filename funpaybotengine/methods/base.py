from __future__ import annotations

__all__ = ('FunPayMethod', 'MethodReturnType')

from typing import TYPE_CHECKING, Any, Type, Generic, TypeVar
from abc import ABC, abstractmethod
from http import HTTPMethod, HTTPStatus

from pydantic import Field, BaseModel
from funpayparsers.parsers.base import ParsingOptions, FunPayObjectParser

from funpaybotengine.base import BindableObject

MethodReturnType = TypeVar('MethodReturnType', bound=Any)


class FunPayMethod(BindableObject, BaseModel, Generic[MethodReturnType], ABC):
    """Base method class."""

    url: str
    """Method URL."""

    method: HTTPMethod = HTTPMethod.GET
    """
    HTTP Method.

    Defaults to ``HTTPMethod.GET``.
    """

    headers: dict[str, str] = Field(default_factory=dict)
    """
    Headers.

    Defaults to empty dict.
    """

    data: dict[str, str] = Field(default_factory=dict)
    """
    Additional data.

    Defaults to empty dict.
    """

    expected_status_codes: list[int | HTTPStatus] = [HTTPStatus.OK]
    """
    List of expected status codes.

    Defaults to ``[HTTPStatus.OK]``.
    """

    parser_cls: Type[FunPayObjectParser] | None = None
    """
    Parser class (not an instance!) for parsing raw source.

    Defaults to ``None``.
    """

    parser_options: ParsingOptions | None = None
    """
    Instance of parser options for ``FunPayMethod.parser_cls``.

    Defaults to ``None``.
    """

    timeout: int | float = 10.0
    """
    Request timeout.

    Defaults to ``10.0``.
    """

    if TYPE_CHECKING:
        def __init__(self,
                     url: str,
                     method: HTTPMethod = HTTPMethod.GET,
                     headers: dict[str, str] = {},
                     data: dict[str, str] = {},
                     expected_status_codes: list[int | HTTPStatus] = [HTTPStatus.OK],
                     parser_cls: Type[FunPayObjectParser] | None = None,
                     parser_options: ParsingOptions | None = None,
                     timeout: float = 10.0):
            """
            :param url: Method URL.
            :param method: HTTP Method.
                Defaults to ``HTTPMethod.GET``.
            :param headers: Headers.
                Defaults to empty dict.
            :param data: Additional data.
                Defaults to empty dict.
            :param expected_status_codes: List of expected status codes.
                Defaults to ``[HTTPStatus.OK]``.
            :param parser_cls: Parser class (not an instance!) for parsing raw source.
                Defaults to ``None``.
            :param parser_options: Instance of parser options for
                ``FunPayMethod.parser_cls``.
                Defaults to ``None``.
            :param timeout: Request timeout.
                Defaults to ``10.0``.
            """

    def model_post_init(self, context: Any, /) -> None:
        super(BindableObject, self).model_post_init(context)
        if self.parser_cls and self.parser_options is None:
            self.parser_options = self.parser_cls.get_options_cls()()

    def parse_result(self, response: str):
        """
        Method that parses raw response.

        By default, this method will use ``FunPayMethod.parser_cls`` and
        ``FunPayMethod.parser_options`` to parse raw response, if
        ``FunPayMethod.parser_cls`` is specified.

        If ``FunPayMethod.parser_options`` is not specified, it will be
        generated automatically.

        If ``FunPayMethod.parser_cls`` not specified, returns raw response.

        :param response: raw response.  # todo: not a string, but an object!
        """
        if self.parser_cls is None:
            return response

        return self.parser_cls(response, options=self.parser_options).parse()

    @abstractmethod
    def transform_result(self, result: Any) -> MethodReturnType:
        """
        Transforms a raw response or parser output
        (i.e., the result of ``FunPayMethod.parse_result``)
        into a type expected by or compatible with funpaybotengine
        (``MethodReturnType``).
        """
        ...
