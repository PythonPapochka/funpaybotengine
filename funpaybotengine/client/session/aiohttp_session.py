from __future__ import annotations

__all__ = ('AioHttpSession',)


from dataclasses import replace
from aiohttp import ClientSession
import asyncio
from funpaybotengine.client.session.base import BaseSession
from typing import TYPE_CHECKING
from http import HTTPStatus, HTTPMethod
if TYPE_CHECKING:
    from funpaybotengine.methods.base import FunPayMethod, MethodReturnType


class AioHttpSession(BaseSession):
    def __init__(self, proxy: str, golden_key: str):
        super().__init__()

        self._proxy_str = proxy
        self._golden_key = golden_key

        self._session = None

    async def session(self) -> ClientSession:
        if self._session is None or self._session.closed:
            self._session = ClientSession(proxy=self.proxy_str)
            self._session.cookie_jar.update_cookies({'golden_key': self.golden_key})
        return self._session

    async def close(self):
        if self._session is not None and not self._session.closed:
            await self._session.close()

            # https://docs.aiohttp.org/en/stable/client_advanced.html#graceful-shutdown
            await asyncio.sleep(0.25)

    async def make_request(self, method: FunPayMethod[MethodReturnType], timeout: float | None = None) -> MethodReturnType:
        session = await self.session()
        timeout = replace(session.timeout, total=timeout if timeout is not None else method.timeout)

        if method.method == HTTPMethod.GET:
            response = await session.get(method.url, params=method.data, timeout=timeout)
        elif method.method == HTTPMethod.POST:
            response = await session.post(method.url, data=method.data, timeout=timeout)
        else:
            raise Exception('Unsupported HTTP method')  # todo: Custom exception

        self.check_status_code(method.expected_status_codes, response.status)
        result = method.parse_result(await response.text())
        return method.transform_result(result)

    def check_status_code(self, expected: list[int | HTTPStatus], status_code: int | HTTPStatus):
        if status_code in expected:
            return

        # todo: custom exceptions for status codes like 429, 404, etc.

        if status_code >= HTTPStatus.INTERNAL_SERVER_ERROR:
            raise Exception('FunPay internal error')  # todo: custom exceptions


    @property
    def proxy_str(self) -> str:
        return self._proxy_str

    @property
    def golden_key(self) -> str:
        return self._golden_key