"""
Instagram Posts dataset.

Posts from Instagram.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class InstagramPosts(BaseDataset):
    """Instagram Posts dataset."""

    DATASET_ID = "gd_lk5ns7kz21pck8jpis"
    NAME = "instagram_posts"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
