"""
World Zipcodes dataset.

Global postal/zip code information.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class WorldZipcodes(BaseDataset):
    """World Zipcodes dataset."""

    DATASET_ID = "gd_licvqc95ta2552qxu"
    NAME = "world_zipcodes"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
