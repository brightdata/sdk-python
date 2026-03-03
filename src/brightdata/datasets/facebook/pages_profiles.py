"""
Facebook Pages Profiles dataset.

Facebook page profiles with page details, follower counts, and category information.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class FacebookPagesProfiles(BaseDataset):
    """FacebookPagesProfiles dataset."""

    DATASET_ID = "gd_mf124a0511bauquyow"
    NAME = "facebook_pages_profiles"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
