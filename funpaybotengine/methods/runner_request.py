from __future__ import annotations


__all__ = ('RunnerRequest',)

from collections.abc import Sequence
from typing import Literal

from pydantic import BaseModel
from funpayparsers.parsers import UpdatesParser

from funpaybotengine.types import RunnerResponse
from funpaybotengine.types.enums import Language
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.types.requests import RunnerRequestData, RequestableObject, Action
from funpaybotengine.client.session.http_methods import HTTPMethod


class RunnerRequest(FunPayMethod[RunnerResponse], BaseModel):
    """
    Get info from runner (``https://funpay.com/runner``).

    Returns ``funpaybotengine.types.UpdatesPack`` obj.
    """

    objects_to_request: Sequence[RequestableObject] | Literal[False] = False
    action: Action | Literal[False] = False

    __model_to_build__ = RunnerResponse

    def __init__(self, request: RunnerRequestData, locale: Language | None = None):
        super().__init__(
            url='runner/',
            method=HTTPMethod.POST,
            locale=locale,
            parser_cls=UpdatesParser,
            data=request.serialize_as_request_data(),
            headers={'X-Requested-With': 'XMLHttpRequest'},
            request=request,
        )
