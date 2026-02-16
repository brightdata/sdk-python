"""
Zillow Properties dataset.

Real estate property listings from Zillow.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class ZillowProperties(BaseDataset):
    """Zillow Properties dataset."""

    DATASET_ID = "gd_lfqkr8wm13ixtbd8f5"
    NAME = "zillow_properties"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
