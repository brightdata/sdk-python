"""
Facebook Group Posts dataset.

Posts from Facebook groups with content, reactions, and comment counts.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.engine import AsyncEngine


class FacebookGroupPosts(BaseDataset):
    """FacebookGroupPosts dataset."""

    DATASET_ID = "gd_lz11l67o2cb3r0lkj3"
    NAME = "facebook_group_posts"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
