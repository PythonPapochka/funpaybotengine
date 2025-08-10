from __future__ import annotations


__all__ = ('FunPayMethod', 'MethodReturnType')

from typing import TYPE_CHECKING, Any, Type, Generic, TypeVar
from abc import ABC
from http import HTTPStatus
from email.utils import parsedate_to_datetime

from pydantic import Field, BaseModel, ConfigDict
from funpayparsers.parsers.base import ParsingOptions, FunPayObjectParser

from funpaybotengine.client.session.http_methods import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.types.enums import Language
    from funpaybotengine.client.session.base import Response
    from funpaybotengine.client.bot import Bot


MethodReturnType = TypeVar('MethodReturnType', bound=Any)


class FunPayMethod(BaseModel, Generic[MethodReturnType], ABC):
    """Base method class."""

    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    url: str
    """Method URL."""

    method: HTTPMethod
    """
    HTTP Method.
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
    Whether this method can be executed as anonymous user or not.
    
    Defaults to ``False``.
    """

    allow_uninitialized: bool = False
    """
    Whether this method can be executed as uninitialized user or not.
    
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
    Additional context for building a final `funpaybotengine` object.
    
    Defaults to empty dict.
    """

    __model_to_build__: Type[MethodReturnType] | None = None

    def model_post_init(self, context: Any, /) -> None:
        if self.parser_cls and self.parser_options is None:
            self.parser_options = self.parser_cls.get_options_cls()()

    def parse_result(self, response: Response[Any]) -> Any:
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

        return self.parser_cls(response.raw_response, options=self.parser_options).parse()

    def transform_result(self, parsing_result: Any, response: Response[Any]) -> MethodReturnType:
        """
        Transforms a raw response or parser output
        (i.e., the result of ``FunPayMethod.parse_result``)
        into a type expected by or compatible with funpaybotengine
        (``MethodReturnType``).
        """
        if self.__model_to_build__ is not None and issubclass(self.__model_to_build__, BaseModel):
            return self.__model_to_build__.model_validate(
                parsing_result, context=self.get_context(response),
            )
        raise NotImplementedError(
            f"{self.__class__.__name__} must either define a BaseModel in '__model_to_build__' "
            f"or override 'transform_result'. "
            f"Currently, '__model_to_build__' is {self.__model_to_build__}, and "
            f"'transform_result' has not been overridden.",
        )

    def to_obj(self, response: Response[Any]) -> MethodReturnType:
        parsing_result = self.parse_result(response)
        return self.transform_result(parsing_result, response)

    def get_context(
        self, response: Response[Any], context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        context = context or {}
        context_from_response: dict[str, Any] = {}

        if 'date' in response.headers:
            context_from_response['response_timestamp'] = parsedate_to_datetime(
                response.headers['date'],
            ).timestamp()

        return self.context | context_from_response | context

    async def execute(self, as_: Bot) -> MethodReturnType:
        result = await as_.make_request(self)
        return result.response_obj
