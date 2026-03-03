"""
Apple App Store Reviews dataset.

Apple App Store reviews dataset.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class AppleAppStoreReviews(BaseDataset):
    """AppleAppStoreReviews dataset."""

    DATASET_ID = "gd_m734msue16e0adkbit"
    NAME = "apple_app_store_reviews"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
