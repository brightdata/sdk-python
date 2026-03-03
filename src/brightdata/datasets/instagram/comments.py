"""
Instagram Comments dataset.

Comments from Instagram posts with text, likes, and commenter information.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class InstagramComments(BaseDataset):
    """InstagramComments dataset."""

    DATASET_ID = "gd_ltppn085pokosxh13"
    NAME = "instagram_comments"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
