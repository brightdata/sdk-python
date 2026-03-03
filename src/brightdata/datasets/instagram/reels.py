"""
Instagram Reels dataset.

Instagram Reels video content with views, likes, and engagement data.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class InstagramReels(BaseDataset):
    """InstagramReels dataset."""

    DATASET_ID = "gd_lyclm20il4r5helnj"
    NAME = "instagram_reels"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
