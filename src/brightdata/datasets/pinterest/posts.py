"""
Pinterest Posts dataset.

Posts/pins from Pinterest.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class PinterestPosts(BaseDataset):
    """Pinterest Posts dataset."""

    DATASET_ID = "gd_lk0sjs4d21kdr7cnlv"
    NAME = "pinterest_posts"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
