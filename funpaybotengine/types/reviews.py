from __future__ import annotations


__all__ = ('Review', 'ReviewsBatch')


from pydantic import BaseModel
from funpayparsers.types import Review as PReview, ReviewsBatch as PReviewsBatch

from funpaybotengine.types.base import FunPayObject
from funpaybotengine.types.common import MoneyValue


class Review(FunPayObject, BaseModel, PReview):
    """
    Represents a review.

    Reviews can be found on the seller’s page or on the order detail page.

    .. note::
        This dataclass does not include a field for review visibility for two reasons:

        1. Reviews appear in two contexts: on seller pages (public)
           and on private order detail pages (visible only to the involved parties).
           Visibility status is available only on private order pages.
           To maintain consistency, this field was omitted.

        2. The HTML structure of reviews is almost identical in both contexts,
           while the visibility flag is located outside the review’s main div.
           Therefore, visibility is handled in the dataclass representing
           the order page (``funpayparsers.types.pages.OrderPage``).
    """

    order_total: MoneyValue | None
    """
    Approximate total amount of the order this review refers to.

    .. note::
        This value may be significantly rounded and should be considered
        only as an estimate, not the exact order total.
    """


class ReviewsBatch(FunPayObject, BaseModel, PReviewsBatch):
    """
    Represents a single batch of reviews.

    This batch contains a portion of all available reviews (typically 25),
    along with metadata required to fetch the next batch.
    """

    reviews: tuple[Review, ...]  # type: ignore[assignment]  # override for model
    """List of reviews included in this batch."""
