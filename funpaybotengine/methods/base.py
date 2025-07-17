from __future__ import annotations


__all__ = ('FunPayMethod', 'MethodReturnType')

from typing import TYPE_CHECKING, Any, Type, Generic, TypeVar
from abc import ABC, abstractmethod
from http import HTTPMethod, HTTPStatus
from pydantic import Field, BaseModel
from funpayparsers.parsers.base import ParsingOptions, FunPayObjectParser

from funpaybotengine.base import BindableObject


if TYPE_CHECKING:
    from funpaybotengine.types.enums import Language


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

    locale: Language | None = None
    """
    FunPay locale.

    If specified and ``FunPayMethod.ignore_locale`` is ``False``,
    it will override bots locale when making a request.

    Defaults to ``None``.
    """

    ignore_locale: bool = False
    """
    Whether to ignore locale or not.
    
    If ``True``, ``FunPayMethod.locale`` will be ignored.
    """

    headers: dict[str, str] = Field(default_factory=dict)
    """
    Headers.

    Defaults to empty dict.
    """

    data: dict[str, Any] = Field(default_factory=dict)
    """
    Additional data.

    Defaults to empty dict.
    """

    expected_status_codes: list[int | HTTPStatus] = [HTTPStatus.OK]
    """
    List of expected status codes.

    Defaults to ``[HTTPStatus.OK]``.
    """

    allow_anonymous: bool = False
    """
    Whether this method can be executed anonymous or not.
    
    Defaults to ``False``.
    """

    parser_cls: Type[FunPayObjectParser] | None = None  # type: ignore[type-arg]
    # unsupported by pydantic
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

    context: dict[str, Any] = Field(default_factory=dict)
    """
    Context for final object.
    
    Defaults to empty dict.
    """

    if TYPE_CHECKING:

        def __init__(
            self,
            url: str,
            method: HTTPMethod = HTTPMethod.GET,
            locale: Language | None = None,
            ignore_locale: bool = False,
            headers: dict[str, str] = {},
            data: dict[str, Any] = {},
            expected_status_codes: list[int | HTTPStatus] = [HTTPStatus.OK],
            allow_anonymous: bool = False,
            parser_cls: Type[FunPayObjectParser[Any, Any]] | None = None,
            parser_options: ParsingOptions | None = None,
            timeout: float = 10.0,
            context: dict[str, Any] = {},
        ):
            """
            :param url: Method URL.
            :param method: HTTP Method.
                Defaults to ``HTTPMethod.GET``.
            :param locale: FunPay locale.
                If specified and ``ignore_locale`` is ``False``,
                it will override bots locale when making a request.
                Defaults to ``None``.
            :param ignore_locale: Whether to ignore locale or not.
                If ``True``, ``FunPayMethod.locale`` will be ignored.
            :param headers: Headers.
                Defaults to empty dict.
            :param data: Additional data.
                Defaults to empty dict.
            :param expected_status_codes: List of expected status codes.
                Defaults to ``[HTTPStatus.OK]``.
            :param allow_anonymous: Whether this method can be executed anonymous
                or not.
                Defaults to ``False``.
            :param parser_cls: Parser class (not an instance!) for parsing raw source.
                Defaults to ``None``.
            :param parser_options: Instance of parser options for
                ``FunPayMethod.parser_cls``.
                Defaults to ``None``.
            :param timeout: Request timeout.
                Defaults to ``10.0``.
            :param context: Context for final object.
                Defaults to empty dict.
            """
            ...

    def model_post_init(self, context: Any, /) -> None:
        super(BindableObject, self).model_post_init(context)
        if self.parser_cls and self.parser_options is None:
            self.parser_options = self.parser_cls.get_options_cls()()

    def parse_result(self, response: str) -> Any:
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

    def to_obj(self, response: str) -> MethodReturnType:
        parsing_result = self.parse_result(response)
        return self.transform_result(parsing_result)
