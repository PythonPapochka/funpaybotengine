from __future__ import annotations


__all__ = ('UploadImage',)


import json
from io import BytesIO
from http import HTTPMethod

from pydantic import BaseModel

from funpaybotengine.methods.base import FunPayMethod


class UploadImage(FunPayMethod[int], BaseModel):
    """
    Uploads chat image (``https://funpay.com/``).

    Returns image ID (``int``).
    """

    def __init__(self, file: str | BytesIO, locale: str = ''):
        super().__init__(
            method=HTTPMethod.POST,
            url='file/addChatImage',
            locale=locale,
            data={'file': open(file, 'rb') if isinstance(file, str) else file},
            headers={'X-Requested-With': 'XMLHttpRequest'},
        )

    def transform_result(self, result: str) -> int:
        return json.loads(result)['fileId']
