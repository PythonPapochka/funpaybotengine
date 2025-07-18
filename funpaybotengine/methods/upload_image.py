from __future__ import annotations


__all__ = ('UploadImage',)


import json
from typing import cast
from io import BytesIO

from pydantic import BaseModel

from funpaybotengine.types.enums import Language
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session.http_methods import HTTPMethod


class UploadImage(FunPayMethod[int], BaseModel):
    """
    Uploads chat image (``https://funpay.com/``).

    Returns image ID (``int``).
    """

    file: str | BytesIO
    """Image stream or path to image to upload."""

    def __init__(self, file: str | BytesIO, locale: Language | None = None):
        super().__init__(
            method=HTTPMethod.POST,
            url='file/addChatImage',
            locale=locale,
            data={'file': open(file, 'rb') if isinstance(file, str) else file},
            headers={'X-Requested-With': 'XMLHttpRequest'},
            file=file,
        )

    def transform_result(self, result: str) -> int:
        return cast(int, json.loads(result)['fileId'])
