"""
Amazon Walmart dataset.

Amazon product data cross-referenced with Walmart for price comparison and availability.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.engine import AsyncEngine


class AmazonWalmart(BaseDataset):
    """AmazonWalmart dataset."""

    DATASET_ID = "gd_m4l6s4mn2g2rkx9lia"
    NAME = "amazon_walmart"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
