"""
Toys R Us Products dataset.

Toy product listings from Toys R Us.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class ToysRUsProducts(BaseDataset):
    """Toys R Us Products dataset."""

    DATASET_ID = "gd_lemuapao1lkjggvn05"
    NAME = "toysrus_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
