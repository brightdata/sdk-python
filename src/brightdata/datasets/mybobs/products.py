"""
Mybobs Products dataset.

Furniture product listings from Bob's Discount Furniture.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class MybobsProducts(BaseDataset):
    """Mybobs Products dataset."""

    DATASET_ID = "gd_lf14k1zw1l3zcxs9m4"
    NAME = "mybobs_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
