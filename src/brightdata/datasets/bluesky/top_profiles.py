"""
Bluesky Top Profiles dataset.

Top 500 Bluesky profiles dataset.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.engine import AsyncEngine


class BlueskyTopProfiles(BaseDataset):
    """BlueskyTopProfiles dataset."""

    DATASET_ID = "gd_m45p78dl1m017wi5lj"
    NAME = "bluesky_top_profiles"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
