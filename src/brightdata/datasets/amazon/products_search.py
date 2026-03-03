"""
Amazon Products Search dataset.

Amazon product search results with listings, prices, and relevance data.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class AmazonProductsSearch(BaseDataset):
    """AmazonProductsSearch dataset."""

    DATASET_ID = "gd_lwdb4vjm1ehb499uxs"
    NAME = "amazon_products_search"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
