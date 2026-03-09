"""
Best Buy Products dataset.

Best Buy products dataset.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.engine import AsyncEngine


class BestBuyProducts(BaseDataset):
    """BestBuyProducts dataset."""

    DATASET_ID = "gd_ltre1jqe1jfr7cccf"
    NAME = "bestbuy_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
