"""
Facebook Profiles dataset.

Facebook user profiles with personal info, friends count, and activity data.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.engine import AsyncEngine


class FacebookProfiles(BaseDataset):
    """FacebookProfiles dataset."""

    DATASET_ID = "gd_mf0urb782734ik94dz"
    NAME = "facebook_profiles"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
