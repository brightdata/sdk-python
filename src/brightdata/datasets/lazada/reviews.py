"""
Lazada Reviews dataset.

Product reviews from Lazada with ratings, text, and reviewer information.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.engine import AsyncEngine


class LazadaReviews(BaseDataset):
    """LazadaReviews dataset."""

    DATASET_ID = "gd_lub6mys21lzcklkq1z"
    NAME = "lazada_reviews"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
