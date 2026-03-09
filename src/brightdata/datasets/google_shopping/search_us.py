"""
Google Shopping Search US dataset.

Google Shopping products search US dataset.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.engine import AsyncEngine


class GoogleShoppingSearchUS(BaseDataset):
    """GoogleShoppingSearchUS dataset."""

    DATASET_ID = "gd_m31f2k0d2m1bah4f3b"
    NAME = "google_shopping_search_us"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
