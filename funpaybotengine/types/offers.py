from __future__ import annotations


__all__ = ('OfferPreview', 'OfferSeller', 'OfferFields')


from typing import Annotated
from types import MappingProxyType
from collections.abc import Mapping

from pydantic import Field, BaseModel, BeforeValidator
from funpayparsers.types import (
    OfferFields as POfferFields,
    OfferSeller as POfferSeller,
    OfferPreview as POfferPreview,
)

from funpaybotengine.types.base import FunPayObject, FunPayMutableObject
from funpaybotengine.types.common import MoneyValue


class OfferSeller(FunPayObject, BaseModel, POfferSeller):
    """Represents the seller of an offer."""

    ...


class OfferPreview(FunPayObject, BaseModel, POfferPreview):
    """Represents an offer preview."""

    price: MoneyValue
    """The price of the offer."""

    seller: OfferSeller | None
    """Information about the offer seller, if applicable."""

    other_data: Annotated[
        Mapping[str, str | int], BeforeValidator(OfferPreview._convert_to_immutable)
    ]
    """
    Additional data related to the offer, such as server ID, side ID, etc., 
    if applicable.
    """

    other_data_names: Annotated[
        Mapping[str, str], BeforeValidator(OfferPreview._convert_to_immutable)
    ]
    """
    Human-readable names corresponding to entries in ``other_data``, if applicable.
    
    Not all entries, that are exists in ``OfferPreview.other_data`` can be found here
    (not all entries have a name).
    """

    @staticmethod
    def _convert_to_immutable(value):
        return MappingProxyType(value)


class OfferFields(FunPayMutableObject, BaseModel, POfferFields):
    """
    Represents the full set of form fields used to construct or update
    an offer on FunPay.

    This class acts as a wrapper around a dictionary of raw form field values
    and provides properties for commonly used fields.

    It is **strongly recommended** to modify offer fields via
    class properties (e.g. ``title_ru``, ``active``, ``images``),
    as they handle proper value formatting and conversions expected by FunPay.

    If no property exists for a particular field,
    use ``set_field(key, value)`` to set it manually,
    making sure to pass a value already formatted for FunPay.

    Setting a field to ``None`` via a property or ``set_field()``
    will automatically remove the corresponding key from ``fields_dict``.

    Examples:
        >>> fields = OfferFields(raw_source='{}', fields_dict={})
        >>> fields.title_ru = "My Offer Name"
        >>> fields.fields_dict
        {'fields[summary][ru]': 'My Offer Name'}
        >>> fields.title_ru = None
        >>> fields.fields_dict
        {}
        >>> fields.active = True
        >>> fields.fields_dict
        {'active': 'on'}
    """

    fields_dict: dict[str, str] = Field(default_factory=dict)
    """All fields as dict."""
