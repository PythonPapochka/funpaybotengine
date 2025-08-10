from __future__ import annotations


__all__ = ('UploadImage',)


import json
from typing import TYPE_CHECKING, Any, cast
from io import BytesIO

from pydantic import BaseModel

from funpaybotengine.types.enums import Language
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session.http_methods import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.client.session.base import Response


class UploadImage(FunPayMethod[int], BaseModel):
    """
    Uploads chat image (``https://funpay.com/``).

    Returns image ID (``int``).
    """

    file: str | BytesIO
    """Image stream or path to image to upload."""

    def __init__(self, file: str | BytesIO, locale: Language | None = None):
        super().__init__(
            url='file/addChatImage',
            method=HTTPMethod.POST,
            locale=locale,
            data={'file': open(file, 'rb') if isinstance(file, str) else file},
            headers={'X-Requested-With': 'XMLHttpRequest'},
            file=file,
        )

    def transform_result(self, parsing_result: str, response: Response[Any]) -> int:
        return cast(int, json.loads(parsing_result)['fileId'])
