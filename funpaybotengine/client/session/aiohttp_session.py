from __future__ import annotations


__all__ = ('AioHttpSession',)


import asyncio
from typing import TYPE_CHECKING
from http import HTTPMethod

from aiohttp import ClientSession, ClientTimeout
from aiohttp.hdrs import USER_AGENT

from funpaybotengine.client.session.base import BaseSession


if TYPE_CHECKING:
    from funpaybotengine.methods.base import FunPayMethod, MethodReturnType
    from funpaybotengine.client.base_bot import BaseBot


class AioHttpSession(BaseSession):
    def __init__(
        self,
        proxy: str | None = None,
        default_headers: dict[str, str] | None = None,
    ):
        super().__init__()

        self._proxy = proxy
        self._default_headers = (
            default_headers
            if default_headers is not None
            else {
                USER_AGENT: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) '
                'Gecko/20100101 Firefox/140.0',
            }
        )

        self._session = None

    async def session(self) -> ClientSession:
        if self._session is None or self._session.closed:
            self._session = ClientSession(
                proxy=self.proxy, base_url='https://funpay.com'
            )
        return self._session

    async def close(self):
        if self._session is not None and not self._session.closed:
            await self._session.close()

            # https://docs.aiohttp.org/en/stable/client_advanced.html#graceful-shutdown
            await asyncio.sleep(0.25)

    async def make_request(
        self,
        method: FunPayMethod[MethodReturnType],
        bot: BaseBot | None = None,
        timeout: float | None = None,
    ) -> MethodReturnType:
        if bot is not None:
            method.bind_to(bot)

        session = await self.session()
        session.cookie_jar.update_cookies({'golden_key': method.bot.golden_key})

        timeout = ClientTimeout(
            total=timeout if timeout is not None else method.timeout
        )

        if method.method == HTTPMethod.GET:
            response = await session.get(
                self.resolve_url(method),
                params=method.data,
                timeout=timeout,
                headers=self._default_headers | method.headers,
            )
        elif method.method == HTTPMethod.POST:
            response = await session.post(
                self.resolve_url(method),
                data=method.data,
                timeout=timeout,
                headers=self._default_headers | method.headers,
            )
        else:
            raise Exception('Unsupported HTTP method')  # todo: Custom exception

        self.check_status_code(method, response.status)

        return method.to_obj(await response.text())

    def resolve_url(self, method: FunPayMethod) -> str:
        if method.ignore_locale:
            locale = ''
        elif method.locale is not None:
            locale = method.locale
        else:
            locale = method.bot.locale

        return f'{locale}/{method.url[1 if method.url.startswith("/") else 0 :]}'

    @property
    def proxy(self) -> str | None:
        return self._proxy
