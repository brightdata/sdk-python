"""
TikTok Posts dataset.

TikTok video posts with captions, view counts, and engagement metrics.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class TikTokPosts(BaseDataset):
    """TikTokPosts dataset."""

    DATASET_ID = "gd_lu702nij2f790tmv9h"
    NAME = "tiktok_posts"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
