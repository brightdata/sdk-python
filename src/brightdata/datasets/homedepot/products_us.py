"""
Home Depot US Products dataset.

Home Depot US products dataset.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class HomeDepotUSProducts(BaseDataset):
    """HomeDepotUSProducts dataset."""

    DATASET_ID = "gd_lmusivh019i7g97q2n"
    NAME = "homedepot_us_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
