"""
YouTube Videos dataset.

Video posts from YouTube.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class YouTubeVideos(BaseDataset):
    """YouTube Videos dataset."""

    DATASET_ID = "gd_lk56epmy2i5g7lzu0k"
    NAME = "youtube_videos"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
