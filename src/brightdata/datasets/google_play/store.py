"""
Google Play Store dataset.

Google Play Store apps dataset.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.engine import AsyncEngine


class GooglePlayStore(BaseDataset):
    """GooglePlayStore dataset."""

    DATASET_ID = "gd_lsk382l8xei8vzm4u"
    NAME = "google_play_store"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
