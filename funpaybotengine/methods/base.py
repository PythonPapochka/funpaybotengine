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

    locale: str = ''
    """
    FunPay locale (``'en'`` / ``'uk'``).

    If specified and ``FunPayMethod.ignore_locale`` is ``False``,
    it will be considered when constructing the final URL via the
    ``full_url`` property.

    Defaults to ``''`` (Russian).
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
            locale: str = '',
            ignore_locale: bool = False,
            headers: dict[str, str] = {},
            data: dict[str, str] = {},
            expected_status_codes: list[int | HTTPStatus] = [HTTPStatus.OK],
            parser_cls: Type[FunPayObjectParser] | None = None,
            parser_options: ParsingOptions | None = None,
            timeout: float = 10.0,
            context: dict[str, Any] = {},
        ):
            """
            :param url: Method URL.
            :param method: HTTP Method.
                Defaults to ``HTTPMethod.GET``.
            :param locale: FunPay locale (``'en'`` / ``'uk'``).
                If specified and ``FunPayMethod.ignore_locale`` is ``False``,
                it will be considered when constructing the final URL via the
                ``full_url`` property.
                Defaults to ``''`` (Russian).
            :param ignore_locale: Whether to ignore locale or not.
                If ``True``, ``FunPayMethod.locale`` will be ignored.
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
            :param context: Context for final object.
                Defaults to empty dict.
            """
            ...

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

    @property
    def full_url(self) -> str:
        """URL with locale."""

        if self.ignore_locale or not self.locale:
            return self.url
        return f'{self.locale}/{self.url[1 if self.url.startswith("/") else 0 :]}'
