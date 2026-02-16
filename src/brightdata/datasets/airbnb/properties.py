"""
Airbnb Properties dataset.

Property listings from Airbnb.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class AirbnbProperties(BaseDataset):
    """Airbnb Properties dataset."""

    DATASET_ID = "gd_ld7ll037kqy322v05"
    NAME = "airbnb_properties"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
