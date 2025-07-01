from funpaybotengine.client.session.base import BaseSession


class Bot:
    def __init__(self,
                 golden_key: str,
                 session: BaseSession | None = None):
        self._golden_key = golden_key
        self._session = session or BaseSession()


    @property
    def golden_key(self) -> str:
        return self._golden_key

    @property
    def session(self) -> BaseSession:
        return self.session
