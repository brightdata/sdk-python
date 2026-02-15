"""
Moynat Products dataset.

Luxury product listings from Moynat.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.async_engine import AsyncEngine


class MoynatProducts(BaseDataset):
    """Moynat Products dataset."""

    DATASET_ID = "gd_lh7rh0d12qkaid87e1"
    NAME = "moynat_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
