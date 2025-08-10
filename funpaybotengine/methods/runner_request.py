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
import json


class RunnerRequest(FunPayMethod[RunnerResponse], BaseModel):
    """
    Get info from runner (``https://funpay.com/runner``).

    Returns ``funpaybotengine.types.UpdatesPack`` obj.
    """

    objects_to_request: Sequence[RequestableObject] | Literal[False] = False
    action: Action | Literal[False] = False

    __model_to_build__ = RunnerResponse

    def __init__(
            self,
            objects_to_request: Sequence[RequestableObject] | Literal[False] = False,
            action: Action | Literal[False] = False,
            locale: Language | None = None
    ):
        super().__init__(
            url='runner/',
            method=HTTPMethod.POST,
            locale=locale,
            parser_cls=UpdatesParser,
            data=self.serialize_as_request_data(objects_to_request, action),
            headers={'X-Requested-With': 'XMLHttpRequest'},

            objects_to_request=objects_to_request,
            action=action
        )

    def serialize_as_request_data(
            self,
            objects_to_request: Sequence[RequestableObject] | Literal[False] = False,
            action: Action | Literal[False] = False,
    ) -> dict[str, str | None]:
        """Returns a dictionary suitable for runner HTTP requests."""
        return {
            'objects': json.dumps(
                [i.model_dump(exclude_none=True, by_alias=True) for i in objects_to_request],
            )
            if objects_to_request
            else 'false',
            'request': action.model_dump_json(exclude_none=True, by_alias=True)
            if action
            else 'false',
        }
