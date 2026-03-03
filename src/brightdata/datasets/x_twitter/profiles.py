"""
X (formerly Twitter) Profiles dataset.

X (formerly Twitter) profiles dataset.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class XTwitterProfiles(BaseDataset):
    """XTwitterProfiles dataset."""

    DATASET_ID = "gd_lwxmeb2u1cniijd7t4"
    NAME = "x_twitter_profiles"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
