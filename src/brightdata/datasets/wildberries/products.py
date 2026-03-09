"""
Wildberries Products dataset.

Wildberries.ru products dataset.

Use get_metadata() to discover all available fields dynamically.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from ..base import BaseDataset

if TYPE_CHECKING:
    from ...core.engine import AsyncEngine


class WildberriesProducts(BaseDataset):
    """WildberriesProducts dataset."""

    DATASET_ID = "gd_luz4fboh2dicd27hhm"
    NAME = "wildberries_products"

    def __init__(self, engine: "AsyncEngine"):
        super().__init__(engine)
        self._fields_by_category: Optional[Dict[str, List[str]]] = None
