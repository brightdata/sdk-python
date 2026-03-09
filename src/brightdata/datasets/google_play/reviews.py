"""
Google Play Reviews dataset.

Google Play Store reviews dataset.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.engine import AsyncEngine


class GooglePlayReviews(BaseDataset):
    """GooglePlayReviews dataset."""

    DATASET_ID = "gd_m6zagkt024uwvvwuyu"
    NAME = "google_play_reviews"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
