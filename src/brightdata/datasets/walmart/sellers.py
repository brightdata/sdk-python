"""
Walmart Sellers Info dataset.

Walmart seller profiles with ratings, product counts, and business information.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.engine import AsyncEngine


class WalmartSellersInfo(BaseDataset):
    """WalmartSellersInfo dataset."""

    DATASET_ID = "gd_m7ke48w81ocyu4hhz0"
    NAME = "walmart_sellers_info"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
