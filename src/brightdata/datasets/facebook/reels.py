"""
Facebook Reels dataset.

Facebook Reels video content with views, reactions, and engagement metrics.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class FacebookReels(BaseDataset):
    """FacebookReels dataset."""

    DATASET_ID = "gd_lyclm3ey2q6rww027t"
    NAME = "facebook_reels"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
