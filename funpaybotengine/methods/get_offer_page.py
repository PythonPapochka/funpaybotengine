from __future__ import annotations


__all__ = ('GetOfferPage',)


from pydantic import BaseModel
from funpayparsers.types import Language
from funpayparsers.parsers.page_parsers import OfferPageParser

from funpaybotengine.types.pages import OfferPage
from funpaybotengine.methods.base import FunPayMethod
from funpaybotengine.client.session import HTTPMethod


class GetOfferPage(FunPayMethod[OfferPage], BaseModel):
    """
    Get an order page method (``https://funpay.com/<lots/chips>/offer?id=<offer_id>``).

    Returns ``funpaybotengine.types.pages.OfferPage`` obj.
    """

    offer_id: int | str

    __model_to_build__ = OfferPage

    def __init__(self, offer_id: int | str, locale: Language | None = None):
        super().__init__(
            url=f'{"lots" if isinstance(offer_id, int) else "chips"}/offer',
            data={'id': str(offer_id)},
            method=HTTPMethod.GET,
            parser_cls=OfferPageParser,
            allow_anonymous=True,
            allow_uninitialized=True,
            locale=locale,
            offer_id=offer_id,
        )
