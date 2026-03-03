"""
Apple App Store dataset.

Apple App Store apps dataset.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class AppleAppStore(BaseDataset):
    """AppleAppStore dataset."""

    DATASET_ID = "gd_lsk9ki3u2iishmwrui"
    NAME = "apple_app_store"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
