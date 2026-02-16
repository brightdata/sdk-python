"""
YouTube Profiles dataset.

Channel profiles from YouTube.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class YouTubeProfiles(BaseDataset):
    """YouTube Profiles dataset."""

    DATASET_ID = "gd_lk538t2k2p1k3oos71"
    NAME = "youtube_profiles"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
