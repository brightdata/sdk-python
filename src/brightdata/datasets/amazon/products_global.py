"""
Amazon Products Global dataset.

Amazon product data across global marketplaces with localized pricing and availability.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.engine import AsyncEngine


class AmazonProductsGlobal(BaseDataset):
    """AmazonProductsGlobal dataset."""

    DATASET_ID = "gd_lwhideng15g8jg63s7"
    NAME = "amazon_products_global"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
