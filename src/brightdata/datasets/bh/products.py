"""
B&H Photo Products dataset.

B&H Photo products dataset.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class BHProducts(BaseDataset):
    """BHProducts dataset."""

    DATASET_ID = "gd_mkce0sox1mchrlpp8g"
    NAME = "bh_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
