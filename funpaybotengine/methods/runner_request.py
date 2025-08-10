from __future__ import annotations


__all__ = ('RunnerRequest',)

from pydantic import BaseModel
from funpayparsers.parsers import UpdatesParser

from funpaybotengine.types import RunnerResponse
from funpaybotengine.types.enums import Language
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.types.requests import RunnerRequestData
from funpaybotengine.client.session.http_methods import HTTPMethod


class RunnerRequest(FunPayMethod[RunnerResponse], BaseModel):
    """
    Get info from runner (``https://funpay.com/runner``).

    Returns ``funpaybotengine.types.UpdatesPack`` obj.
    """

    request: RunnerRequestData
    """Runner request data."""

    __model_to_build__ = RunnerResponse

    def __init__(self, request: RunnerRequestData):
        super().__init__(
            url='runner/',
            method=HTTPMethod.POST,
            ignore_locale=True,
            parser_cls=UpdatesParser,
            data=request.serialize_as_request_data(),
            headers={'X-Requested-With': 'XMLHttpRequest'},

            request=request,
        )
