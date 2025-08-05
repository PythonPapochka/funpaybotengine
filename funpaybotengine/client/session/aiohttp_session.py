from __future__ import annotations


__all__ = ('AioHttpSession',)


import time
import asyncio
from typing import TYPE_CHECKING, Any

from yarl import URL
from aiohttp import ClientSession, ClientTimeout
from aiohttp.hdrs import USER_AGENT
from aiohttp import TCPConnector

from funpaybotengine.loggers import session_logger
from funpaybotengine.client.session.base import Response, BaseSession
from funpaybotengine.client.session.http_methods import HTTPMethod


if TYPE_CHECKING:
    from funpaybotengine.client.bot import Bot
    from funpaybotengine.methods.base import FunPayMethod, MethodReturnType


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

        self._connector: TCPConnector | None = None

    async def session(self) -> ClientSession:
        if self._connector is None or self._connector.closed:
            self._connector = TCPConnector()
        return ClientSession(
            proxy=self.proxy,
            base_url='https://funpay.com',
            connector=self._connector,
            connector_owner=False
        )

    async def close(self) -> None:
        if self._connector is not None and not self._connector.closed:
            await self._connector.close()

            # https://docs.aiohttp.org/en/stable/client_advanced.html#graceful-shutdown
            await asyncio.sleep(0.25)

    def _prepare_method(
            self,
            method: FunPayMethod[MethodReturnType],
            bot: Bot | None,
    ) -> None:
        if bot is not None:
            method.bind_to(bot)

        if method.bot is None:
            raise Exception('Method is unbound')  # todo

        if not method.allow_anonymous and method.bot.anonymous:
            raise Exception(
                f"Method '{method.__class__.__name__}' cannot be executed as an anonymous user. ",
            )  # todo

    async def make_request(
        self,
        method: FunPayMethod[MethodReturnType],
        bot: Bot | None = None,
        timeout: float | None = None,
    ) -> Response[MethodReturnType]:
        if bot is not None:
            method.bind_to(bot)

        if method.bot is None:
            raise Exception('Method is unbound')  # todo

        if not method.allow_anonymous and method.bot.anonymous:
            raise Exception(
                f"Method '{method.__class__.__name__}' cannot be executed as an anonymous user. ",
            )  # todo

        session = await self.session()
        session.cookie_jar.clear()
        session.cookie_jar.update_cookies({'cookie_prefs': '1'})  # no 3rd-party cookies
        if method.bot.golden_key:
            session.cookie_jar.update_cookies({'golden_key': method.bot.golden_key})
        if method.bot.phpsessid:
            session.cookie_jar.update_cookies({'PHPSESSID': method.bot.phpsessid})

        timeout_obj = ClientTimeout(total=timeout if timeout is not None else method.timeout)

        url_to_log = (
            method.url
            if URL(method.url).is_absolute()
            else str(session._base_url.join(URL(self.resolve_url(method))))  # type: ignore[union-attr]
        )

        session_logger.info(f'Making {method.method.name} request to {url_to_log}')
        start_time = time.time()

        async with session:
            if method.method == HTTPMethod.GET:
                response = await session.get(
                    self.resolve_url(method),
                    params=method.data,
                    timeout=timeout_obj,
                    headers=self._default_headers | method.headers,
                )
            elif method.method == HTTPMethod.POST:
                response = await session.post(
                    self.resolve_url(method),
                    data=method.data,
                    timeout=timeout_obj,
                    headers=self._default_headers | method.headers,
                )
            else:
                raise Exception('Unsupported HTTP method')  # todo: Custom exception

        session_logger.debug(
            f'Requesting {url_to_log} took {time.time() - start_time}s. Status: {response.status}.',
        )

        self.check_status_code(method, response.status)

        cookies: dict[str, str] = {}
        if response.history:
            for i in response.history:
                cookies = cookies | {k: v.value for k, v in i.cookies.items()}
        else:
            cookies = {k: v.value for k, v in response.cookies.items()}

        output = Response(
            url=str(response.real_url),
            status_code=response.status,
            raw_response=await response.text(),
            response_obj=None,
            response_headers={k.lower(): v for k, v in response.headers.items()},
            response_cookies=cookies,
            method_obj=method,
        )

        start_time = time.time()
        result = method.to_obj(output)
        output.response_obj = result
        session_logger.debug(f'Parsing response of {url_to_log} took {time.time() - start_time}s.')
        return output

    def resolve_url(self, method: FunPayMethod[Any]) -> str:
        if method.ignore_locale:
            locale = ''
        elif method.locale is not None:
            locale = method.locale.value.url_alias
        else:
            locale = method.bot.locale.value.url_alias  # type: ignore[union-attr] # always has bound bot

        if locale == 'ru':
            locale = ''

        return f'{locale}/{method.url[1 if method.url.startswith("/") else 0 :]}'

    @property
    def proxy(self) -> str | None:
        return self._proxy
