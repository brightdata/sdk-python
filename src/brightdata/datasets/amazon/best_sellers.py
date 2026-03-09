"""
Amazon Best Sellers dataset.

Amazon best-selling products with rankings, categories, and sales data.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.engine import AsyncEngine


class AmazonBestSellers(BaseDataset):
    """AmazonBestSellers dataset."""

    DATASET_ID = "gd_l1vijixj9g2vp7563"
    NAME = "amazon_best_sellers"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
