"""
Google Shopping Products dataset.

Google Shopping products dataset.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.engine import AsyncEngine


class GoogleShoppingProducts(BaseDataset):
    """GoogleShoppingProducts dataset."""

    DATASET_ID = "gd_ltppk50q18kdw67omz"
    NAME = "google_shopping_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
