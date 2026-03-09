"""
Facebook Posts By URL dataset.

Facebook posts collected by direct URL with full post content and metadata.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.engine import AsyncEngine


class FacebookPostsByUrl(BaseDataset):
    """FacebookPostsByUrl dataset."""

    DATASET_ID = "gd_lyclm1571iy3mv57zw"
    NAME = "facebook_posts_by_url"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
