"""
Reddit Posts dataset.

Reddit posts dataset.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class RedditPosts(BaseDataset):
    """RedditPosts dataset."""

    DATASET_ID = "gd_lvz8ah06191smkebj4"
    NAME = "reddit_posts"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
