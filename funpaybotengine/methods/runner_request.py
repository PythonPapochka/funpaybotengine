from __future__ import annotations


__all__ = ('RunnerRequest',)

from typing import TYPE_CHECKING

from pydantic import BaseModel
from funpayparsers.parsers import UpdatesParser

from funpaybotengine.types import RunnerResponse
from funpaybotengine.types.enums import Language
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.types.requests import RunnerRequestData
from funpaybotengine.client.session.http_methods import HTTPMethod


if TYPE_CHECKING:
    from funpayparsers.types.pages import MainPage as ParserMainPage


class RunnerRequest(FunPayMethod[RunnerResponse], BaseModel):
    """
    Get info from runner (``https://funpay.com/runner``).

    Returns ``funpaybotengine.types.UpdatesPack`` obj.
    """

    def __init__(self, request: RunnerRequestData, locale: Language | None = None):
        super().__init__(
            url='runner/',
            method=HTTPMethod.POST,
            locale=locale,
            parser_cls=UpdatesParser,
            data=request.serialize_as_request_data(),
            headers={'X-Requested-With': 'XMLHttpRequest'},
        )

    def transform_result(self, result: ParserMainPage) -> RunnerResponse:
        return RunnerResponse.model_validate(result, context={'bot': self._bot})
